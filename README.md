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
+ They are specific to a VPC environment (e.g. dev/stage etc), they are encrypted with environment-specific password, which should be exported in the environment variable: `VAULT_PASSWORD_BUILDENV`

```
export VAULT_PASSWORD_BUILDENV=<'dev/stage/prod' password>
```

## Invocation examples
```
ansible-playbook gold-img-build.yml
```

### Test 
##### Windows
```
$env:PACKER_LOG=1
$env:PACKER_LOG_PATH="packerlog.txt"
.\packer.exe build .\ubuntu1804.json
```
##### Linux
```
set PACKER_LOG=1
set PACKER_LOG_PATH="packerlog.txt"
./packer build ubuntu1804.json
```
