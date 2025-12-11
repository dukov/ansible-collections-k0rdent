# awx_inventories

An Ansible role to create and manage AWX inventory objects using the `awx.awx.inventory` module.

## Description

This role allows you to create, update, or delete AWX inventories defined in variables. Inventories can be configured with organization assignments, descriptions, variables, and inventory sources. Inventory sources can pull inventory data from SCM projects, cloud providers (EC2, GCE, Azure, etc.), or other sources.

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
| `awx_inventories` | List of inventory dictionaries to create | Yes | `[]` |
| `awx_inventory_defaults` | Default values for inventories | No | See defaults/main.yml |
| `awx_host` | AWX host address (from `CONTROLLER_HOST` env var) | No | `localhost` |
| `awx_username` | AWX API username (from `CONTROLLER_USERNAME` env var) | No | `admin` |
| `awx_password` | AWX API password (from `CONTROLLER_PASSWORD` env var) | No | `""` |
| `awx_token` | AWX API OAuth token (from `CONTROLLER_OAUTH_TOKEN` env var, alternative to password) | No | `""` |
| `awx_validate_certs` | Validate SSL certificates | No | `true` |

**Note**: AWX connection parameters (`awx_host`, `awx_username`, `awx_password`, `awx_token`) are automatically read from environment variables (`CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD`, `CONTROLLER_OAUTH_TOKEN`). If not set, defaults are used.

### Inventory Dictionary Structure

Each item in the `awx_inventories` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the inventory | Yes | - |
| `organization` | Organization name | No | - |
| `description` | Description of the inventory | No | - |
| `variables` | Inventory variables in YAML or JSON format | No | - |
| `inventory_sources` | List of inventory sources for this inventory | No | - |
| `state` | State (present/absent) | No | `present` |

#### Inventory Source Dictionary Structure

Each item in the `inventory_sources` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the inventory source | Yes | - |
| `source` | Source type (scm, ec2, gce, azure_rm, vmware, openstack, etc.) | No | - |
| `source_project` | Project name for SCM-based sources | No | - |
| `source_path` | Path within the project for SCM-based sources | No | - |
| `credential` | Credential name for the source | No | - |
| `overwrite` | Overwrite variables | No | `false` |
| `overwrite_vars` | Overwrite variables | No | `false` |
| `update_on_launch` | Update on launch | No | `false` |
| `update_cache_timeout` | Cache timeout in seconds | No | - |
| `source_vars` | Source-specific variables | No | - |
| `state` | State (present/absent) | No | `present` |

## Dependencies

- `awx.awx` collection

## Example Playbook

### Basic Example - Single Inventory

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
  roles:
    - awx_inventories
```

### Multiple Inventories

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
      - name: "Staging Inventory"
        organization: "Staging"
        description: "Staging environment inventory"
      - name: "Development Inventory"
        organization: "Development"
        description: "Development environment inventory"
  roles:
    - awx_inventories
```

### Inventory with Variables

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
        variables: |
          ansible_user: admin
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          cluster_name: production
  roles:
    - awx_inventories
```

### Inventory with JSON Variables

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
        variables: |
          {
            "ansible_user": "admin",
            "ansible_ssh_common_args": "-o StrictHostKeyChecking=no",
            "cluster_name": "production"
          }
  roles:
    - awx_inventories
```

### Inventory with Variables from Dictionary

```yaml
- hosts: localhost
  vars:
    inventory_vars:
      ansible_user: admin
      ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
      cluster_name: production
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
        variables: "{{ inventory_vars | to_nice_yaml }}"
  roles:
    - awx_inventories
```

### Inventory with SCM-based Inventory Source

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
        inventory_sources:
          - name: "Production Inventory Source"
            source: "scm"
            source_project: "My Ansible Playbooks"
            source_path: "inventories/production.yml"
            update_on_launch: true
            overwrite: true
  roles:
    - awx_inventories
```

### Inventory with Multiple Inventory Sources

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        description: "Production environment inventory"
        inventory_sources:
          - name: "Production SCM Source"
            source: "scm"
            source_project: "My Ansible Playbooks"
            source_path: "inventories/production.yml"
            update_on_launch: true
            overwrite: true
          - name: "Production EC2 Source"
            source: "ec2"
            credential: "AWS Credential"
            source_vars: |
              regions:
                - us-east-1
              filters:
                instance-state-name: running
            update_on_launch: true
            update_cache_timeout: 3600
  roles:
    - awx_inventories
```

### Inventory with EC2 Inventory Source

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "AWS EC2 Inventory"
        organization: "Production"
        description: "Dynamic EC2 inventory"
        inventory_sources:
          - name: "EC2 Dynamic Source"
            source: "ec2"
            credential: "AWS Credential"
            source_vars: |
              regions:
                - us-east-1
                - us-west-2
              filters:
                instance-state-name: running
              keyed_groups:
                - key: tags.Environment
                  prefix: env
            update_on_launch: true
            update_cache_timeout: 1800
  roles:
    - awx_inventories
```

### Inventory with Azure RM Inventory Source

```yaml
- hosts: localhost
  vars:
    awx_inventories:
      - name: "Azure Inventory"
        organization: "Production"
        description: "Dynamic Azure inventory"
        inventory_sources:
          - name: "Azure RM Source"
            source: "azure_rm"
            credential: "Azure Credential"
            source_vars: |
              include_vm_resource_groups:
                - production-rg
                - staging-rg
            update_on_launch: true
  roles:
    - awx_inventories
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
    awx_inventories:
      - name: "My Inventory"
        organization: "Default"
        description: "My inventory"
  roles:
    - awx_inventories
```

Alternatively, you can override the defaults in your playbook:

```yaml
- hosts: localhost
  vars:
    awx_host: "awx.example.com"
    awx_token: "{{ vault_awx_token }}"
    awx_inventories:
      - name: "My Inventory"
        organization: "Default"
        description: "My inventory"
  roles:
    - awx_inventories
```

## License

GPL-3.0-or-later

## Author Information

This role is part of the k0rdent.core Ansible collection.

