# Ansible inventory plugin for Kubernetes nodes
# Reference: https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_inventory.html

DOCUMENTATION = r"""
name: k8s_nodes
plugin_type: inventory
short_description: Kubernetes nodes inventory source
description:
    - Dynamically builds Ansible inventory from Kubernetes nodes using the Kubernetes API.
    - Supports multiple clusters, grouping by labels, and subnet-based ansible_host selection.
options:
    plugin:
        description: Token that ensures this is a source file for the 'k8s_nodes' plugin.
        required: true
        choices:
            - k0rdent.core.k8s_nodes
            - k8s_nodes
    kubeconfig:
        description: Path to kubeconfig file to use for authentication.
        required: false
        type: path
    context:
        description: Kubeconfig context to use.
        required: false
        type: str
    ansible_subnet:
        description: >-
            Subnet (in CIDR notation) to select which node IP address to use for ansible_host. If not set, falls back to InternalIP or ExternalIP.
        required: false
        type: str
    clusters:
        description:
            - List of clusters to inventory. Each cluster can specify its name, namespace, type (capi or adopted), kubeconfig secret, ansible_subnet, and host_groups.
        required: true
        type: list
        elements: dict
        suboptions:
            name:
                description: Name of the cluster.
                required: true
                type: str
            namespace:
                description: Namespace of the cluster.
                required: true
                type: str
            type:
                description: Cluster type, either 'capi' or 'adopted'.
                required: true
                type: str
                choices:
                    - capi
                    - adopted
            kubeconfig_secret:
                description: >-
                    (For adopted clusters) Secret reference for kubeconfig. Dict with keys: name, namespace, key.
                required: false
                type: dict
            ansible_subnet:
                description: Subnet (CIDR) to use for ansible_host for this cluster (overrides global ansible_subnet).
                required: false
                type: str
            host_groups:
                description: >-
                    List of host group definitions for grouping hosts by label values. Each item is a dict with 'key' (label key) and 'group_prefix'.
                required: false
                type: list
                elements: dict
                suboptions:
                    key:
                        description: Node label key to group by.
                        required: true
                        type: str
                    group_prefix:
                        description: Prefix to prepend to group name for this label.
                        required: true
                        type: str
    host_groups:
        description: >-
            (Optional) List of global host group definitions for grouping hosts by label values. Each item is a dict with 'key' and 'group_prefix'.
        required: false
        type: list
        elements: dict
        suboptions:
            key:
                description: Node label key to group by.
                required: true
                type: str
            group_prefix:
                description: Prefix to prepend to group name for this label.
                required: true
                type: str
author:
    - dukov
seealso:
    - module: community.kubernetes.k8s_info
    - module: community.kubernetes.k8s
notes:
    - Requires the kubernetes Python client library.
    - Supports grouping hosts by arbitrary node labels.
    - ansible_host is set based on ansible_subnet, InternalIP, or ExternalIP.
    - For CAPI clusters, kubeconfig secret is auto-determined by convention.
    - For adopted clusters, kubeconfig_secret must be provided.
"""

import ipaddress
import base64
import yaml

from typing import Any, Dict, Optional, Mapping
from dataclasses import dataclass
from enum import Enum

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.group import to_safe_group_name

from kubernetes import client, config

NODE_RESOURCE_KIND = "node"
CAPI_KUBECONFIG_SECRET_KEY = "value"
CAPI_KUBECONFIG_SUFFIX = "-kubeconfig"


@dataclass
class Resource:
    group: str
    version: str
    kind: str
    namespace: Optional[str] = None
    label_selector: Optional[str] = None
    plural: Optional[str] = None


@dataclass
class HostGroup:
    key: str
    group_prefix: str


class ClusterType(str, Enum):
    CAPI: str = "capi"
    ADOPTED: str = "adopted"


@dataclass
class KubeConfigSecret:
    name: str
    namespace: str
    key: str


@dataclass
class Cluster:
    name: str
    namespace: str
    type: ClusterType
    kubeconfig_secret: Optional[KubeConfigSecret] = None
    ansible_subnet: Optional[str] = None
    host_groups: Optional[list[HostGroup]] = None

    def __post_init__(self):
        if self.kubeconfig_secret:
            self.kubeconfig_secret = KubeConfigSecret(**self.kubeconfig_secret)
        self.host_groups = [HostGroup(**item) for item in self.host_groups]


@dataclass
class Config:
    plugin: str
    ansible_subnet: str
    clusters: list[Cluster]
    host_groups: Optional[list[HostGroup]]
    kubeconfig: Optional[str] = None
    context: Optional[str] = None

    def __post_init__(self):
        self.clusters = [Cluster(**item) for item in self.clusters]
        self.host_groups = [HostGroup(**item) for item in self.host_groups]


class InventoryModule(BaseInventoryPlugin):
    NAME: str = "k0rdent.core.k8s_nodes"

    def verify_file(self, path: str) -> bool:
        """Verify file is usable by this plugin."""
        if super(InventoryModule, self).verify_file(path):
            return True
        return False

    def parse(
        self, inventory: Any, loader: DataLoader, path: str, cache: bool = True
    ) -> None:
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        config_data: Mapping[str, Any] = self._read_config_data(path)
        cfg = Config(**config_data)

        try:
            if cfg.kubeconfig:
                config.load_kube_config(config_file=cfg.kubeconfig, context=cfg.context)
            else:
                config.load_incluster_config()
        except Exception as e:
            raise AnsibleError("Failed to read kubernetes config: %s" % e)

        # Ensure the group exists before adding hosts
        if self.NAME not in self.inventory.groups:
            self.inventory.add_group(self.NAME)

        all_nodes = []
        for cluster in cfg.clusters:
            if cluster.type == ClusterType.ADOPTED:
                # We must have it for adopted clusters
                assert cluster.kubeconfig_secret is not None
                api_client = self.get_client_from_secret(cluster.kubeconfig_secret)
            elif cluster.type == ClusterType.CAPI:
                # TODO we need a better way to determine kubeconfig secret for capi clusters
                api_client = self.get_client_from_secret(
                    KubeConfigSecret(
                        name=f"{cluster.name}{CAPI_KUBECONFIG_SUFFIX}",
                        namespace=cluster.namespace,
                        key=CAPI_KUBECONFIG_SECRET_KEY,
                    )
                )

            nodes = self.get_k8s_nodes(api_client=api_client)
            all_nodes += nodes["items"]
            self.add_nodes(nodes["items"], cfg.ansible_subnet, cluster)

    def add_nodes(self, nodes: list, ansible_subnet: str, cluster: Cluster) -> None:
        config_net = ansible_subnet
        if cluster.ansible_subnet:
            config_net = cluster.ansible_subnet

        # Ensure the group exists before adding hosts
        cluster_group_name = to_safe_group_name(
            f"{cluster.namespace}__{cluster.name}", force=True
        )
        namespace_group_name = to_safe_group_name(cluster.namespace, force=True)
        for group in [cluster_group_name, namespace_group_name]:
            if group not in self.inventory.groups:
                self
                self.inventory.add_group(group)

        for node in nodes:
            name: str = node["metadata"]["name"]
            self.inventory.add_host(name, group=self.NAME)
            self.inventory.add_host(name, group=cluster_group_name)
            self.inventory.add_host(name, group=namespace_group_name)

            # TODO we may want ti make it configurable
            node_labels = node["metadata"].get("labels", {})

            # Add host to  Ansible host groups we use value of the key specified in config as
            # a group name ans prepend it with prefix if configured e.g.
            # - key: cluster.x-k8s.io/cluster-name
            #   prefix: ""
            # will result into hosts grouped by cluster names
            host_groups = cluster.host_groups or []
            for host_group in host_groups:
                if host_group.key in node_labels:
                    # format is <cluster name>_<host group prefix value><label values>
                    group_name = to_safe_group_name(
                        f"{cluster.namespace}__{cluster.name}__{host_group.group_prefix}{node_labels[host_group.key]}",
                        force=True,
                    )
                    if group_name not in self.inventory.groups:
                        self.inventory.add_group(group_name)
                    self.inventory.add_host(name, group=group_name)

            hostvars: Dict[str, Any] = {
                "labels": node_labels,
                #'annotations': node['metadata'].get('annotations', {}),
                "internal_ip": None,
                "external_ip": None,
                "os_image": node["status"].get("nodeInfo", {}).get("osImage", ""),
                "kubelet_version": node["status"]
                .get("nodeInfo", {})
                .get("kubeletVersion", ""),
            }
            ansible_host_ip = None
            addresses = node["status"].get("addresses", [])
            # TODO this should be refactored to pull all ip addresses
            for addr in addresses:
                if addr["type"] == "InternalIP":
                    hostvars["internal_ip"] = addr["address"]
                elif addr["type"] == "ExternalIP":
                    hostvars["external_ip"] = addr["address"]

                try:
                    if ipaddress.ip_address(addr["address"]) in ipaddress.ip_network(
                        config_net, strict=False
                    ):
                        ansible_host_ip = addr["address"]
                except Exception:
                    pass

            # If ansible_subnet matched, use that, else fallback to internal_ip or external_ip
            if ansible_host_ip:
                hostvars["ansible_host"] = ansible_host_ip
            elif hostvars["internal_ip"]:
                hostvars["ansible_host"] = hostvars["internal_ip"]
            elif hostvars["external_ip"]:
                hostvars["ansible_host"] = hostvars["external_ip"]

            for k, v in hostvars.items():
                self.inventory.set_variable(name, k, v)

    def get_resources(
        self,
        resource: Resource,
    ) -> Any:
        """
        Query Kubernetes custom resources using the dynamic client, with optional label filtering.
        :param group: API group of the custom resource
        :param version: API version
        :param plural: Plural name of the resource
        :param namespace: Namespace (optional)
        :param label_selector: Label selector for filtering (optional)
        :return: List of custom resources
        """
        if resource.kind.lower() == NODE_RESOURCE_KIND:
            return self.get_k8s_nodes(label_selector=resource.label_selector)

        plural = resource.plural or f"{resource.kind.lower()}s"
        api = client.CustomObjectsApi()
        if resource.namespace:
            return api.list_namespaced_custom_object(
                resource.group,
                resource.version,
                resource.namespace,
                plural,
                label_selector=resource.label_selector,
            )
        else:
            return api.list_cluster_custom_object(
                resource.group,
                resource.version,
                plural,
                label_selector=resource.label_selector,
            )

    def get_client_from_secret(
        self,
        secret_ref: KubeConfigSecret,
        api_client: Optional[client.ApiClient] = None,
    ) -> client.ApiClient:
        v1 = client.CoreV1Api(api_client=api_client)
        secret = v1.read_namespaced_secret(secret_ref.name, secret_ref.namespace)
        kubeconfig_yaml = base64.b64decode(secret.data.get(secret_ref.key, ""))
        kubeconfig_dict = yaml.safe_load(kubeconfig_yaml)
        return config.new_client_from_config_dict(kubeconfig_dict)

    def get_k8s_nodes(
        self,
        label_selector: Optional[str] = None,
        api_client: Optional[client.ApiClient] = None,
    ) -> Any:
        """
        Query Kubernetes nodes using the CoreV1Api, with optional label filtering.
        :param label_selector: Label selector for filtering (optional)
        :return: List of node resources (dict)
        """
        v1 = client.CoreV1Api(api_client=api_client)

        return v1.list_node(label_selector=label_selector).to_dict()
