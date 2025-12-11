# awx_projects

An Ansible role to create and manage AWX project objects using the `awx.awx.project` module.

## Description

This role allows you to create, update, or delete AWX projects defined in variables. Projects can be configured with various SCM (Source Control Management) settings including Git, SVN, Mercurial, and more.

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
| `awx_projects` | List of project dictionaries to create | Yes | `[]` |
| `awx_project_defaults` | Default values for projects | No | See defaults/main.yml |
| `awx_host` | AWX host address (from `CONTROLLER_HOST` env var) | No | `localhost` |
| `awx_username` | AWX API username (from `CONTROLLER_USERNAME` env var) | No | `admin` |
| `awx_password` | AWX API password (from `CONTROLLER_PASSWORD` env var) | No | `""` |
| `awx_token` | AWX API OAuth token (from `CONTROLLER_OAUTH_TOKEN` env var, alternative to password) | No | `""` |
| `awx_validate_certs` | Validate SSL certificates | No | `true` |

**Note**: AWX connection parameters (`awx_host`, `awx_username`, `awx_password`, `awx_token`) are automatically read from environment variables (`CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD`, `CONTROLLER_OAUTH_TOKEN`). If not set, defaults are used.

### Project Dictionary Structure

Each item in the `awx_projects` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the project | Yes | - |
| `scm_type` | SCM type (git, svn, hg, insights, archive) | No | `git` |
| `scm_url` | URL of the SCM repository | No | - |
| `scm_branch` | Branch to use for the project | No | - |
| `scm_refspec` | Refspec to use for the project | No | - |
| `scm_credential` | Name of the credential to use for SCM | No | - |
| `organization` | Organization name | No | - |
| `description` | Description of the project | No | - |
| `scm_clean` | Clean the SCM checkout before update | No | - |
| `scm_delete_on_update` | Delete the SCM checkout before update | No | - |
| `scm_track_submodules` | Track submodules | No | - |
| `scm_update_on_launch` | Update project on launch | No | - |
| `scm_update_cache_timeout` | Cache timeout in seconds | No | - |
| `state` | State (present/absent) | No | `present` |

## Dependencies

- `awx.awx` collection

## Example Playbook

### Basic Example - Single Project

```yaml
- hosts: localhost
  vars:
    awx_projects:
      - name: "My Ansible Playbooks"
        scm_type: "git"
        scm_url: "https://github.com/example/ansible-playbooks.git"
        scm_branch: "main"
        organization: "Default"
        description: "Main repository for Ansible playbooks"
  roles:
    - awx_projects
```

### Multiple Projects

```yaml
- hosts: localhost
  vars:
    awx_projects:
      - name: "Production Playbooks"
        scm_type: "git"
        scm_url: "https://github.com/example/prod-playbooks.git"
        scm_branch: "production"
        organization: "Production"
        scm_update_on_launch: true
        description: "Production environment playbooks"
      - name: "Staging Playbooks"
        scm_type: "git"
        scm_url: "https://github.com/example/staging-playbooks.git"
        scm_branch: "staging"
        organization: "Staging"
        scm_update_on_launch: true
        description: "Staging environment playbooks"
      - name: "Development Playbooks"
        scm_type: "git"
        scm_url: "https://github.com/example/dev-playbooks.git"
        scm_branch: "develop"
        organization: "Development"
  roles:
    - awx_projects
```

### Project with SCM Credential

```yaml
- hosts: localhost
  vars:
    awx_projects:
      - name: "Private Repository"
        scm_type: "git"
        scm_url: "https://github.com/example/private-repo.git"
        scm_branch: "main"
        scm_credential: "GitHub Credential"
        organization: "Default"
        scm_update_on_launch: true
        description: "Private repository requiring authentication"
  roles:
    - awx_projects
```

### Project with Advanced SCM Settings

```yaml
- hosts: localhost
  vars:
    awx_projects:
      - name: "Advanced Git Project"
        scm_type: "git"
        scm_url: "https://github.com/example/ansible-playbooks.git"
        scm_branch: "main"
        scm_refspec: "+refs/heads/*:refs/remotes/origin/*"
        scm_clean: true
        scm_delete_on_update: false
        scm_track_submodules: true
        scm_update_on_launch: true
        scm_update_cache_timeout: 3600
        organization: "Default"
        description: "Git project with advanced SCM settings"
  roles:
    - awx_projects
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
    awx_projects:
      - name: "My Project"
        scm_type: "git"
        scm_url: "https://github.com/example/ansible-playbooks.git"
        scm_branch: "main"
        organization: "Default"
  roles:
    - awx_projects
```

Alternatively, you can override the defaults in your playbook:

```yaml
- hosts: localhost
  vars:
    awx_host: "awx.example.com"
    awx_token: "{{ vault_awx_token }}"
    awx_projects:
      - name: "My Project"
        scm_type: "git"
        scm_url: "https://github.com/example/ansible-playbooks.git"
        scm_branch: "main"
        organization: "Default"
  roles:
    - awx_projects
```

## License

GPL-3.0-or-later

## Author Information

This role is part of the k0rdent.core Ansible collection.

