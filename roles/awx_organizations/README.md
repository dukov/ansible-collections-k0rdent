# awx_organizations

An Ansible role to create and manage AWX organization objects using the `awx.awx.organization` module.

## Description

This role allows you to create, update, or delete AWX organizations defined in variables. Organizations are used to group and manage resources (projects, inventories, credentials, etc.) in AWX, providing isolation and access control.

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
| `awx_organizations` | List of organization dictionaries to create | Yes | `[]` |
| `awx_organization_defaults` | Default values for organizations | No | See defaults/main.yml |
| `awx_host` | AWX host address (from `CONTROLLER_HOST` env var) | No | `localhost` |
| `awx_username` | AWX API username (from `CONTROLLER_USERNAME` env var) | No | `admin` |
| `awx_password` | AWX API password (from `CONTROLLER_PASSWORD` env var) | No | `""` |
| `awx_token` | AWX API OAuth token (from `CONTROLLER_OAUTH_TOKEN` env var, alternative to password) | No | `""` |
| `awx_validate_certs` | Validate SSL certificates | No | `true` |

**Note**: AWX connection parameters (`awx_host`, `awx_username`, `awx_password`, `awx_token`) are automatically read from environment variables (`CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD`, `CONTROLLER_OAUTH_TOKEN`). If not set, defaults are used.

### Organization Dictionary Structure

Each item in the `awx_organizations` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the organization | Yes | - |
| `description` | Description of the organization | No | - |
| `max_hosts` | Maximum number of hosts allowed in this organization | No | - |
| `custom_virtualenv` | Custom virtual environment path | No | - |
| `galaxy_credentials` | List of Galaxy credential names | No | - |
| `instance_groups` | List of instance group names | No | - |
| `state` | State (present/absent) | No | `present` |

## Dependencies

- `awx.awx` collection

## Example Playbook

### Basic Example - Single Organization

```yaml
- hosts: localhost
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment organization"
  roles:
    - awx_organizations
```

### Multiple Organizations

```yaml
- hosts: localhost
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment organization"
        max_hosts: 1000
      - name: "Staging"
        description: "Staging environment organization"
        max_hosts: 500
      - name: "Development"
        description: "Development environment organization"
        max_hosts: 100
  roles:
    - awx_organizations
```

### Organization with Instance Groups

```yaml
- hosts: localhost
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment organization"
        instance_groups:
          - "Production Executors"
          - "High Availability Group"
  roles:
    - awx_organizations
```

### Organization with Galaxy Credentials

```yaml
- hosts: localhost
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment organization"
        galaxy_credentials:
          - "Galaxy Credential"
  roles:
    - awx_organizations
```

### Organization with Custom Virtual Environment

```yaml
- hosts: localhost
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment organization"
        custom_virtualenv: "/opt/venv/production"
        max_hosts: 1000
  roles:
    - awx_organizations
```

### Complete Example

```yaml
- hosts: localhost
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment organization"
        max_hosts: 1000
        custom_virtualenv: "/opt/venv/production"
        galaxy_credentials:
          - "Galaxy Credential"
        instance_groups:
          - "Production Executors"
      - name: "Staging"
        description: "Staging environment organization"
        max_hosts: 500
        instance_groups:
          - "Staging Executors"
  roles:
    - awx_organizations
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
    awx_organizations:
      - name: "My Organization"
        description: "My organization"
  roles:
    - awx_organizations
```

Alternatively, you can override the defaults in your playbook:

```yaml
- hosts: localhost
  vars:
    awx_host: "awx.example.com"
    awx_token: "{{ vault_awx_token }}"
    awx_organizations:
      - name: "My Organization"
        description: "My organization"
  roles:
    - awx_organizations
```

## License

GPL-3.0-or-later

## Author Information

This role is part of the k0rdent.core Ansible collection.

