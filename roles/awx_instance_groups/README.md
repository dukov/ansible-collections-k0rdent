# awx_instance_groups

An Ansible role to create and manage AWX instance group objects using the `awx.awx.instance_group` module.

## Description

This role allows you to create, update, or delete AWX instance groups defined in variables. Instance groups are used to organize and manage execution nodes in AWX, and can be configured with policies for instance selection and container group settings.

## Requirements

- Ansible 2.9 or higher
- `awx.awx` collection installed
- Access to AWX/Controller instance

## Environment Variables

The role reads AWX connection parameters from environment variables. Set these before running your playbook:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `CONTROLLER_HOST` | AWX/Controller host address | `localhost` |
| `CONTROLLER_USERNAME` | AWX/Controller API username | `admin` |
| `CONTROLLER_PASSWORD` | AWX/Controller API password | `""` |
| `CONTROLLER_OAUTH_TOKEN` | AWX/Controller API OAuth token (alternative to password) | `""` |

Example:
```bash
export CONTROLLER_HOST="awx.example.com"
export CONTROLLER_USERNAME="admin"
export CONTROLLER_OAUTH_TOKEN="your-oauth-token"
```

## Role Variables

### Main Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `awx_instance_groups` | List of instance group dictionaries to create | Yes | `[]` |
| `awx_instance_group_defaults` | Default values for instance groups | No | See defaults/main.yml |
| `awx_host` | AWX host address (from `CONTROLLER_HOST` env var) | No | `localhost` |
| `awx_username` | AWX API username (from `CONTROLLER_USERNAME` env var) | No | `admin` |
| `awx_password` | AWX API password (from `CONTROLLER_PASSWORD` env var) | No | `""` |
| `awx_token` | AWX API OAuth token (from `CONTROLLER_OAUTH_TOKEN` env var, alternative to password) | No | `""` |
| `awx_validate_certs` | Validate SSL certificates | No | `true` |

**Note**: AWX connection parameters (`awx_host`, `awx_username`, `awx_password`, `awx_token`) are automatically read from environment variables (`CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD`, `CONTROLLER_OAUTH_TOKEN`). If not set, defaults are used.

### Instance Group Dictionary Structure

Each item in the `awx_instance_groups` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the instance group | Yes | - |
| `instances` | List of instance names to add to the group | No | - |
| `policy_instance_minimum` | Minimum number of instances to use | No | - |
| `policy_instance_percentage` | Percentage of instances to use | No | - |
| `policy_instance_list` | List of specific instances for policy | No | - |
| `is_container_group` | Whether this is a container group | No | `false` |
| `pod_spec_override` | Pod specification override for container groups | No | - |
| `state` | State (present/absent) | No | `present` |

## Dependencies

- `awx.awx` collection

## Example Playbook

### Basic Example - Single Instance Group

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "Production Executors"
        instances:
          - "executor-1"
          - "executor-2"
        policy_instance_minimum: 1
  roles:
    - awx_instance_groups
```

### Multiple Instance Groups

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "Production Executors"
        instances:
          - "prod-executor-1"
          - "prod-executor-2"
          - "prod-executor-3"
        policy_instance_minimum: 2
        policy_instance_percentage: 50
      - name: "Staging Executors"
        instances:
          - "staging-executor-1"
          - "staging-executor-2"
        policy_instance_minimum: 1
      - name: "Development Executors"
        instances:
          - "dev-executor-1"
  roles:
    - awx_instance_groups
```

### Instance Group with Policy Configuration

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "High Availability Group"
        instances:
          - "executor-1"
          - "executor-2"
          - "executor-3"
          - "executor-4"
        policy_instance_minimum: 2
        policy_instance_percentage: 75
        policy_instance_list:
          - "executor-1"
          - "executor-2"
  roles:
    - awx_instance_groups
```

### Container Group

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "Kubernetes Container Group"
        is_container_group: true
        pod_spec_override: |
          apiVersion: v1
          kind: Pod
          metadata:
            name: ansible-runner-pod
          spec:
            containers:
              - name: ansible-runner
                image: quay.io/ansible/ansible-runner:latest
                resources:
                  requests:
                    memory: "512Mi"
                    cpu: "500m"
                  limits:
                    memory: "1Gi"
                    cpu: "1000m"
  roles:
    - awx_instance_groups
```

### Container Group with Custom Pod Spec

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "Custom Container Group"
        is_container_group: true
        pod_spec_override: |
          {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
              "name": "custom-ansible-runner",
              "labels": {
                "app": "ansible-runner"
              }
            },
            "spec": {
              "containers": [
                {
                  "name": "ansible-runner",
                  "image": "quay.io/ansible/ansible-runner:latest",
                  "env": [
                    {
                      "name": "ANSIBLE_FORCE_COLOR",
                      "value": "true"
                    }
                  ],
                  "resources": {
                    "requests": {
                      "memory": "1Gi",
                      "cpu": "1000m"
                    },
                    "limits": {
                      "memory": "2Gi",
                      "cpu": "2000m"
                    }
                  }
                }
              ]
            }
          }
  roles:
    - awx_instance_groups
```

### Using AWX Token Authentication

Set environment variables before running the playbook:

```bash
export CONTROLLER_HOST="awx.example.com"
export CONTROLLER_OAUTH_TOKEN="your-oauth-token-here"
```

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "My Instance Group"
        instances:
          - "executor-1"
  roles:
    - awx_instance_groups
```

Alternatively, you can override the defaults in your playbook:

```yaml
- hosts: localhost
  vars:
    awx_host: "awx.example.com"
    awx_token: "{{ vault_awx_token }}"
    awx_instance_groups:
      - name: "My Instance Group"
        instances:
          - "executor-1"
  roles:
    - awx_instance_groups
```

## License

GPL-3.0-or-later

## Author Information

This role is part of the k0rdent.core Ansible collection.

