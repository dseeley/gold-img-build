# gold-img-build
Builds 'golden' image from base iso + yum/apt updates 

## Prerequisites

### Localhost

Dependencies are managed via Pipenv:
```bash
pipenv install
```
Will create a Python virtual environment with dependencies specified in the Pipfile.

To active it, simply enter:
```bash
pipenv shell
```

### Credentials
Credentials are encrypted inline in the playbooks using ansible-vault.  
+ Where they are specific to a VPC environment (e.g. dev/stage etc), they are encrypted with environment-specific password, which should be exported in the environment variable: `VAULT_PASSWORD_BUILDENV`
+ Where they are generic the are exported via `VAULT_PASSWORD_ALL`

```
export VAULT_PASSWORD_ALL=<'all' password>
export VAULT_PASSWORD_BUILDENV=<'dev/stage/prod' password>
```

## Invocation examples
```
ansible-playbook gold-img-build.yml
```
