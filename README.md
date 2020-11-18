# gold-img-build-esxi
Builds a 'gold' esxi server image (currently Ubuntu only) from the base server iso, applies package updates and sets custom network config, using [packer](https://www.packer.io/) (and the `vmware-iso` builder).

Optionally runs within a docker container, and automatically pulls the server images.

Several configurations are provided (in `roles/gold-img-build/templates`):
+ **ubuntu2004**:  Uses the new [autoinstall](https://ubuntu.com/server/docs/install/autoinstall-reference) mechanism
+ **ubuntu2004_legacy**:  Uses the legacy preseeding technology.
+ **ubuntu1804**:  Uses the legacy preseeding technology.

## Prerequisites

### ESXI Config:
+ Enable SSH
  + Inside the web UI, navigate to “Manage”, then the “Services” tab. Find the entry called: “TSM-SSH”, and enable it.
+ Enable “Guest IP Hack”
  + `esxcli system settings advanced set -o /Net/GuestIPHack -i 1`
+ Open VNC Ports on the ESXi firewall (**_only necessary if using esxi < 6.7 and packer < 1.6.4 and not defining `vnc_over_websocket`_**)
    ```
    Packer connects to the VM using VNC, so we’ll open a range of ports to allow it to connect to it.
    
    cat <<EOFVNC >/etc/vmware/firewall/vnc.xml
    <ConfigRoot>
      <!-- Allow inbound VNC for Packer -->
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
    </ConfigRoot>
    EOFVNC
 
    # Update the permissions and reload the firewall:
    
    chmod 444 /etc/vmware/firewall/vnc.xml
    esxcli network firewall refresh
    ```

+ If you are using (or want to use) a non-root account to connect to ESXi:
  + In the UI, navigate to /host/manage/security/users
    + Add a user of your choice, e.g. `svc`
  + In the UI, navigate to /host/, and select Actions/Permissions
    + Click Add User, and add the `svc` user.  Give it Administrator Role.
  + If you want to login using public key:
    + Generate a key pair `ssh-keygen -t rsa -f id_rsa_esxisvc`
    + On the ESXi host, add the ssh directory for the `svc` user: `mkdir /etc/ssh/keys-svc`
    + On the ESXi host, copy the public key (`id_rsa_esxisvc.pub`) to `/etc/ssh/keys-svc/authorized_keys`
    + On the ESXi host, change the permissions of the files: 
      + `chown -R svc: /etc/ssh/keys-svc/`
      + `chmod +t /etc/ssh/keys-svc/authorized_keys`
      + `chmod og-r /etc/ssh/keys-svc/authorized_keys`
    + Restart SSH `/etc/init.d/SSH restart`
    + Make the authorized_keys file persistent:
      + `/sbin/auto-backup.sh`


### Ansible Vault Secrets
Credentials can be encrypted inline in the playbooks using ansible-vault.  They are exposed to ansible via the `vault_password_file` [script mechanism](https://docs.ansible.com/ansible/latest/user_guide/vault.html#storing-passwords-in-third-party-tools-with-vault-password-client-scripts) (defined to point to `.vaultpass-client.py` in the `ansible.cfg` file), which returns the vault password referenced `VAULT_PASSWORD` environment variable.
```
export VAULT_PASSWORD=<password>
```

## Invocation
```
ansible-playbook gold-img-build.yml -e os_id=ubuntu2004
ansible-playbook gold-img-build.yml -e os_id=ubuntu2004 -e copylocal=true -e skip_docker=true
```

### Mandatory command-line variables:
+ `-e os_id=<ubuntu2004>` - an entry under base_os in `defaults/main.yml`

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
