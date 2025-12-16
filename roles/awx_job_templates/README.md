# awx_job_templates

An Ansible role to create and manage AWX job template objects and their schedules using the `awx.awx.job_template` and `awx.awx.schedule` modules.

## Description

This role allows you to create, update, or delete AWX job templates defined in variables. Job templates can be configured with inventories, projects, playbooks, credentials, and various execution options. Additionally, the role supports creating schedules for job templates to enable automated execution.

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
| `awx_job_templates` | List of job template dictionaries to create | Yes | `[]` |
| `awx_job_template_defaults` | Default values for job templates | No | See defaults/main.yml |
| `awx_host` | AWX host address (from `CONTROLLER_HOST` env var) | No | `localhost` |
| `awx_username` | AWX API username (from `CONTROLLER_USERNAME` env var) | No | `admin` |
| `awx_password` | AWX API password (from `CONTROLLER_PASSWORD` env var) | No | `""` |
| `awx_token` | AWX API OAuth token (from `CONTROLLER_OAUTH_TOKEN` env var, alternative to password) | No | `""` |
| `awx_validate_certs` | Validate SSL certificates | No | `true` |

**Note**: AWX connection parameters (`awx_host`, `awx_username`, `awx_password`, `awx_token`) are automatically read from environment variables (`CONTROLLER_HOST`, `CONTROLLER_USERNAME`, `CONTROLLER_PASSWORD`, `CONTROLLER_OAUTH_TOKEN`). If not set, defaults are used.

### Job Template Dictionary Structure

Each item in the `awx_job_templates` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the job template | Yes | - |
| `job_type` | Job type (run, check) | No | `run` |
| `inventory` | Inventory name | No | - |
| `project` | Project name | No | - |
| `playbook` | Playbook path | No | - |
| `credentials` | List of credential names | No | - |
| `organization` | Organization name | No | - |
| `description` | Description of the job template | No | - |
| `extra_vars` | Extra variables in YAML or JSON format | No | - |
| `limit` | Host limit | No | - |
| `verbosity` | Verbosity level (0-5) | No | - |
| `forks` | Number of forks | No | - |
| `timeout` | Job timeout in seconds | No | - |
| `schedules` | List of schedule dictionaries | No | - |
| `state` | State (present/absent) | No | `present` |

#### Schedule Dictionary Structure

Each item in the `schedules` list can contain:

| Key | Description | Required | Default |
|-----|-------------|----------|---------|
| `name` | Name of the schedule | Yes | - |
| `rrule` | Recurrence rule in RFC 5545 format | Yes | - |
| `description` | Description of the schedule | No | - |
| `enabled` | Whether the schedule is enabled | No | `true` |
| `extra_data` | Extra variables for the scheduled job | No | - |
| `state` | State (present/absent) | No | `present` |

**Note on `rrule`**: The recurrence rule must follow RFC 5545 format. Examples:
- Daily: `DTSTART:20240101T000000Z RRULE:FREQ=DAILY;INTERVAL=1`
- Weekly: `DTSTART:20240101T000000Z RRULE:FREQ=WEEKLY;BYDAY=MO;INTERVAL=1`
- Hourly: `DTSTART:20240101T000000Z RRULE:FREQ=HOURLY;INTERVAL=1`
- Every 5 minutes: `DTSTART:20240101T000000Z RRULE:FREQ=MINUTELY;INTERVAL=5`

## Dependencies

- `awx.awx` collection

## Example Playbook

### Basic Example - Single Job Template

```yaml
- hosts: localhost
  vars:
    awx_job_templates:
      - name: "Deploy Application"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "deploy.yml"
        credentials:
          - "SSH Credential"
  roles:
    - awx_job_templates
```

### Job Template with Schedule

```yaml
- hosts: localhost
  vars:
    awx_job_templates:
      - name: "Backup Database"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "backup.yml"
        credentials:
          - "Database Credential"
        schedules:
          - name: "Daily Backup"
            rrule: "DTSTART:20240101T000000Z RRULE:FREQ=DAILY;INTERVAL=1"
            description: "Daily backup at midnight UTC"
            enabled: true
  roles:
    - awx_job_templates
```

### Job Template with Multiple Schedules

```yaml
- hosts: localhost
  vars:
    awx_job_templates:
      - name: "Deploy Application"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "deploy.yml"
        credentials:
          - "SSH Credential"
        schedules:
          - name: "Daily Deployment"
            rrule: "DTSTART:20240101T000000Z RRULE:FREQ=DAILY;INTERVAL=1"
            description: "Daily deployment at midnight UTC"
            enabled: true
          - name: "Weekly Maintenance"
            rrule: "DTSTART:20240101T020000Z RRULE:FREQ=WEEKLY;BYDAY=SU;INTERVAL=1"
            description: "Weekly maintenance on Sundays at 2 AM UTC"
            enabled: true
  roles:
    - awx_job_templates
```

### Job Template with Extra Variables and Schedule

```yaml
- hosts: localhost
  vars:
    awx_job_templates:
      - name: "Deploy Application"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "deploy.yml"
        credentials:
          - "SSH Credential"
        extra_vars: |
          app_version: "1.0.0"
          environment: "production"
        schedules:
          - name: "Daily Deployment"
            rrule: "DTSTART:20240101T000000Z RRULE:FREQ=DAILY;INTERVAL=1"
            description: "Daily deployment at midnight UTC"
            enabled: true
            extra_data: |
              app_version: "latest"
  roles:
    - awx_job_templates
```

### Multiple Job Templates

```yaml
- hosts: localhost
  vars:
    awx_job_templates:
      - name: "Deploy Application"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "deploy.yml"
        credentials:
          - "SSH Credential"
        schedules:
          - name: "Daily Deployment"
            rrule: "DTSTART:20240101T000000Z RRULE:FREQ=DAILY;INTERVAL=1"
            enabled: true
      - name: "Backup Database"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "backup.yml"
        credentials:
          - "Database Credential"
        schedules:
          - name: "Hourly Backup"
            rrule: "DTSTART:20240101T000000Z RRULE:FREQ=HOURLY;INTERVAL=1"
            enabled: true
  roles:
    - awx_job_templates
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
    awx_job_templates:
      - name: "My Job Template"
        job_type: "run"
        inventory: "Production"
        project: "My Project"
        playbook: "deploy.yml"
  roles:
    - awx_job_templates
```

## License

GPL-3.0-or-later

## Author Information

This role is part of the k0rdent.core Ansible collection.

