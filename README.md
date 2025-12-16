# Ansible Collection - k0rdent.core

An Ansible collection for managing AWX (Ansible Automation Platform) resources including organizations, credentials, projects, inventories, instance groups, and job templates.

## Description

This collection provides a set of Ansible roles to automate the configuration and management of AWX/Ansible Automation Platform resources. It enables infrastructure-as-code for AWX, allowing you to define your entire AWX configuration in Ansible playbooks and version control it.

## Requirements

- Ansible 2.9 or higher
- `awx.awx` collection (version >= 24.6.1)
- Access to AWX/Controller instance

## Installation

### Install the Collection

```bash
ansible-galaxy collection install k0rdent.core
```

### Install Dependencies

The collection requires the `awx.awx` collection:

```bash
ansible-galaxy collection install awx.awx
```

## Environment Variables

All roles in this collection read AWX connection parameters from environment variables:

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

## Roles

### awx_organizations

Creates and manages AWX organizations. Automatically creates and assigns Ansible Galaxy credentials to enable collection installation during project sync.

**Key Features:**
- Create/update/delete organizations
- Automatic Ansible Galaxy credential creation and assignment
- Instance group assignment
- Custom virtual environment configuration

**Documentation:** See [roles/awx_organizations/README.md](roles/awx_organizations/README.md)

### awx_credentials

Creates and manages AWX credentials including SSH keys, API tokens, and other credential types.

**Key Features:**
- Support for Machine credentials with SSH keys
- SSH key from file or variable
- Multiple credential types
- Organization assignment

**Documentation:** See [roles/awx_credentials/README.md](roles/awx_credentials/README.md)

### awx_projects

Creates and manages AWX projects with SCM configuration.

**Key Features:**
- Git, SVN, Mercurial, and other SCM types
- Branch and refspec configuration
- SCM credential assignment
- Update on launch settings
- Cache timeout configuration

**Documentation:** See [roles/awx_projects/README.md](roles/awx_projects/README.md)

### awx_inventories

Creates and manages AWX inventories and inventory sources.

**Key Features:**
- Static and dynamic inventories
- SCM-based inventory sources
- Cloud provider inventory sources (EC2, Azure, GCE, etc.)
- Inventory variables
- Update on launch configuration

**Documentation:** See [roles/awx_inventories/README.md](roles/awx_inventories/README.md)

### awx_instance_groups

Creates and manages AWX instance groups for execution node management.

**Key Features:**
- Instance assignment and policies
- Container group configuration
- Kubernetes pod specification with deep merge
- Policy configuration (minimum instances, percentage, etc.)

**Documentation:** See [roles/awx_instance_groups/README.md](roles/awx_instance_groups/README.md)

### awx_job_templates

Creates and manages AWX job templates and their schedules.

**Key Features:**
- Job template creation with full configuration
- Schedule management with RFC 5545 recurrence rules
- Multiple schedules per template
- Extra variables support
- Launch prompt configuration

**Documentation:** See [roles/awx_job_templates/README.md](roles/awx_job_templates/README.md)

## Quick Start

### Example Playbook

```yaml
---
- name: Configure AWX
  hosts: localhost
  connection: local
  vars:
    awx_organizations:
      - name: "Production"
        description: "Production environment"
    
    awx_credentials:
      - name: "Default Machine Credential"
        ssh_key_path: "/path/to/ssh/key"
    
    awx_projects:
      - name: "My Project"
        scm_type: "git"
        scm_url: "https://github.com/example/ansible-playbooks.git"
        scm_branch: "main"
        organization: "Production"
    
    awx_inventories:
      - name: "Production Inventory"
        organization: "Production"
        inventory_sources:
          - name: "Production Source"
            source: "scm"
            source_project: "My Project"
            source_path: "inventories/production.yml"
    
    awx_instance_groups:
      - name: "default"
        is_container_group: true
        pod_spec_override:
          spec:
            containers:
              - name: worker
                image: quay.io/ansible/awx-ee:latest
    
    awx_job_templates:
      - name: "Deploy Application"
        job_type: "run"
        inventory: "Production Inventory"
        project: "My Project"
        playbook: "deploy.yml"
        credentials:
          - "Default Machine Credential"
        schedules:
          - name: "Daily Deployment"
            rrule: "DTSTART:20240101T000000Z RRULE:FREQ=DAILY;INTERVAL=1"
            enabled: true
  
  roles:
    - k0rdent.core.awx_organizations
    - k0rdent.core.awx_credentials
    - k0rdent.core.awx_projects
    - k0rdent.core.awx_inventories
    - k0rdent.core.awx_instance_groups
    - k0rdent.core.awx_job_templates
```

### Execution Order

When using multiple roles, it's recommended to execute them in this order:

1. **awx_organizations** - Create organizations first (needed by other resources)
2. **awx_credentials** - Create credentials (may be needed by projects and job templates)
3. **awx_projects** - Create projects (needed by inventory sources)
4. **awx_inventories** - Create inventories and inventory sources (depends on projects)
5. **awx_instance_groups** - Create instance groups (independent)
6. **awx_job_templates** - Create job templates and schedules (depends on inventories, projects, credentials)

## Usage Examples

### Complete AWX Configuration

See [playbooks/awx_config.yml](playbooks/awx_config.yml) for a complete example of configuring all AWX resources.

### Individual Role Usage

Each role can be used independently. Refer to the individual role README files for detailed examples and parameter documentation.

## License

GPL-3.0-or-later

## Author Information

- **Dmitry Ukov** <dukov@mirantis.com>

## Support

- **Repository:** https://github.com/dukov/ansible-collections-k0rdent
- **Issues:** https://github.com/dukov/ansible-collections-k0rdent/issues

## Version History

- **0.0.1** - Initial release with AWX management roles
