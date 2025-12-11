# awx_credentials

An Ansible role to create and manage AWX credential objects using the `awx.awx.credential` module.

## Description

This role allows you to create, update, or delete AWX credentials defined in variables. By default, it creates 'Machine' type credentials with username 'ansible'. SSH keys can be passed as variables or loaded from files.

## Requirements

- Ansible 2.9 or higher
- `awx.awx` collection installed
- Access to AWX/Tower instance

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
| `awx_credentials` | List of credential dictionaries to create | Yes | `[]` |
| `awx_credential_defaults` | Default values for credentials | No | See defaults/main.yml |
| `awx_host` | AWX host address (from `CONTROLLER_HOST` env var) | No | `localhost` |
| `awx_username` | AWX API username (from `CONTROLLER_USERNAME` env var) | No | `admin` |
| `awx_password` | AWX API password (from `CONTROLLER_PASSWORD` env var) | No | `""` |
| `awx_token` | AWX API OAuth token (from `CONTROLLER_OAUTH_TOKEN` env var, alternative to password) | No | `""` |
| `awx_validate_certs` | Validate SSL certificates | No | `true` |

**Note**: AWX connection parameters (`awx_host`, `awx_username`, `awx_password`, `awx_token`) are automatically read from environment variables (`CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD`, `CONTROLLER_OAUTH_TOKEN`). If not set, defaults are used.

### Credential Dictionary Structure

Each item in the `awx_credentials` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the credential | Yes | - |
| `credential_type` | Type of credential | No | `Machine` |
| `username` | Username for the credential | No | `ansible` |
| `ssh_key` | SSH private key content | No | - |
| `ssh_key_path` | Path to SSH private key file | No | - |
| `organization` | Organization name | No | - |
| `description` | Description of the credential | No | - |
| `state` | State (present/absent) | No | `present` |

**Note**: Either `ssh_key` or `ssh_key_path` can be provided, but not both. If `ssh_key_path` is used, the role will read the file content automatically.

## Dependencies

- `awx.awx` collection

## Example Playbook

### Basic Example - Single Credential

```yaml
- hosts: localhost
  vars:
    awx_credentials:
      - name: "Production SSH Key"
        username: "ansible"
        ssh_key: "{{ lookup('file', '~/.ssh/id_rsa') }}"
        organization: "Default"
        description: "SSH key for production servers"
  roles:
    - awx_credentials
```

### Multiple Credentials

```yaml
- hosts: localhost
  vars:
    awx_credentials:
      - name: "Production Machine Credential"
        username: "ansible"
        ssh_key_path: "~/.ssh/prod_key"
        organization: "Production"
        description: "Production environment credential"
      - name: "Staging Machine Credential"
        username: "ansible"
        ssh_key: "{{ vault_prod_ssh_key }}"
        organization: "Staging"
        description: "Staging environment credential"
      - name: "Development Machine Credential"
        username: "devops"
        ssh_key_path: "~/.ssh/dev_key"
        organization: "Development"
  roles:
    - awx_credentials
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
    awx_credentials:
      - name: "Default Machine Credential"
        username: "ansible"
        ssh_key: "{{ vault_ssh_key }}"
  roles:
    - awx_credentials
```

Alternatively, you can override the defaults in your playbook:

```yaml
- hosts: localhost
  vars:
    awx_host: "awx.example.com"
    awx_token: "{{ vault_awx_token }}"
    awx_credentials:
      - name: "Default Machine Credential"
        username: "ansible"
        ssh_key: "{{ vault_ssh_key }}"
  roles:
    - awx_credentials
```

### Custom Credential Type

```yaml
- hosts: localhost
  vars:
    awx_credentials:
      - name: "GitHub Token"
        credential_type: "Source Control"
        organization: "Default"
        description: "GitHub personal access token"
  roles:
    - awx_credentials
```

## License

GPL-3.0-or-later

## Author Information

This role is part of the k0rdent.core Ansible collection.

