# gold-img-build-esxi
Builds 'golden' esxi image from base iso + yum/apt updates 


## Prerequisites

### ESXI Config:
+ Enable SSH
  + Inside the web UI, navigate to “Manage”, then the “Services” tab. Find the entry called: “TSM-SSH”, and enable it.
+ Enable “Guest IP Hack”
  + `esxcli system settings advanced set -o /Net/GuestIPHack -i 1`
+ Open VNC Ports on the Firewall
    ```
    Packer connects to the VM using VNC, so we’ll open a range of ports to allow it to connect to it.
    
    First, ensure we can edit the firewall configuration:
    
    chmod 644 /etc/vmware/firewall/service.xml
    chmod +t /etc/vmware/firewall/service.xml
    Then append the range we want to open to the end of the file:
    
    <service id="1000">
      <id>packer-vnc</id>
      <rule id="0000">
        <direction>inbound</direction>
        <protocol>tcp</protocol>
        <porttype>dst</porttype>
        <port>
          <begin>5900</begin>
          <end>6000</end>
        </port>
      </rule>
      <enabled>true</enabled>
      <required>true</required>
    </service>
    Finally, restore the permissions and reload the firewall:
    
    chmod 444 /etc/vmware/firewall/service.xml
    esxcli network firewall refresh
    ```


### Credentials
Credentials are encrypted inline in the playbooks using ansible-vault.  
```
export VAULT_PASSWORD=<password>
```

## Invocation
```
ansible-playbook gold-img-build.yml
```

### Optional extra variables:
+ `-e copylocal=true` - Copies the Ubuntu base image and Packer executable from the local Ansible directory, rather than downloading them _(default: false)_.  
+ `-e skip_docker=true` - Run on localhost rather than within a Docker container _(default: false)_.

### Test
If the script fails, there will be a remnant in a `/tmp/ansible.[hash]` directory.  Enter this directory, and run:

#### Windows
```
$env:PACKER_LOG=1
$env:PACKER_LOG_PATH="packerlog.txt"
.\packer.exe build .\ubuntu1804.json
```
#### Linux
```
set PACKER_LOG=1
set PACKER_LOG_PATH="packerlog.txt"
./packer build ubuntu1804.json
```
