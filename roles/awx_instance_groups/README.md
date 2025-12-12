# awx_instance_groups

An Ansible role to create and manage AWX instance group objects using the `awx.awx.instance_group` module.

## Description

This role allows you to create, update, or delete AWX instance groups defined in variables. Instance groups are used to organize and manage execution nodes in AWX, and can be configured with policies for instance selection and container group settings.

For container groups, the role provides a default pod specification that can be customized using `pod_spec_override`. The role uses a deep merge strategy to combine your custom pod specification with the defaults: dictionaries are merged recursively, while lists are completely replaced. This allows you to override specific settings while preserving other default values.

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
| `pod_spec_override` | Pod specification override for container groups (dictionary) | No | - |
| `state` | State (present/absent) | No | `present` |

**Note on `pod_spec_override`**: This variable should be provided as a dictionary (not a YAML string). The role uses a deep merge strategy to combine the default pod specification (`awx_instance_group_defaults.default_pod_spec`) with your custom `pod_spec_override`. When merging:
- **Dictionaries are merged recursively**: Nested dictionary keys from your override will be merged with the default values
- **Lists are overwritten**: If both the default and your override contain a list at the same path, your list will completely replace the default list

This allows you to override specific fields (like container image, resources, or environment variables) while keeping other default values intact.

### Pod Specification Deep Merge Strategy

The role implements a deep merge strategy for `pod_spec_override` using Ansible's `combine` filter with `recursive=true`. This means:

1. **Default Pod Specification**: The role provides a default pod specification in `awx_instance_group_defaults.default_pod_spec` that includes common settings like namespace, service account, and container configuration.

2. **Deep Merge Behavior**:
   - **Dictionary merging**: When you provide a dictionary value that exists in both the default and your override, the values are merged recursively. For example, if the default has `spec.containers[0].resources.requests.cpu: 250m` and you provide `spec.containers[0].resources.requests.memory: 1Gi`, both values will be present in the final result.
   - **List overwriting**: When you provide a list value (like `spec.containers` or `spec.containers[0].env`), your entire list replaces the default list. This is because the `combine` filter does not merge lists, only dictionaries.

3. **Example Merge**:
   ```yaml
   # Default pod spec has:
   spec:
     containers:
       - name: worker
         image: quay.io/ansible/awx-ee:latest
         resources:
           requests:
             cpu: 250m
             memory: 100Mi
   
   # Your override provides:
   pod_spec_override:
     spec:
       containers:
         - name: worker
           resources:
             requests:
               memory: 512Mi
   
   # Result: The entire containers list is replaced, so you must include
   # all container definitions you want. The default container is lost.
   ```

4. **Best Practice**: When overriding container specifications, include the complete container definition in your `pod_spec_override`, or structure your override to only modify dictionary values (like `metadata.labels` or `spec.serviceAccountName`) that will be merged with defaults.

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
        pod_spec_override:
          spec:
            containers:
              - name: worker
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

**Note**: The `pod_spec_override` is merged with the default pod specification. In this example, only the container definition will be overwritten.

```yaml
- hosts: localhost
  vars:
    awx_instance_groups:
      - name: "Custom Container Group"
        is_container_group: true
        pod_spec_override:
          metadata:
            labels:
              app: ansible-runner
          spec:
            serviceAccountName: awx-inventory-reader
            automountServiceAccountToken: true
            containers:
              - name: worker
                image: quay.io/ansible/ansible-runner:latest
                env:
                  - name: ANSIBLE_FORCE_COLOR
                    value: "true"
                resources:
                  requests:
                    memory: "1Gi"
                    cpu: "1000m"
                  limits:
                    memory: "2Gi"
                    cpu: "2000m"
  roles:
    - awx_instance_groups
```

**Note**: This example demonstrates the deep merge behavior:
- The `metadata.labels` dictionary is merged with defaults (if any)
- The `spec.containers` list completely replaces the default containers list (lists are overwritten, not merged)
- The `spec.serviceAccountName` and `spec.automountServiceAccountToken` override the default values
- Other default values (like `apiVersion`, `kind`, `metadata.namespace`) are preserved from the default pod spec

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

