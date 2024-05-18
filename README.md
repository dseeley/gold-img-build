# gold-img-build
Builds 'gold' Ubuntu server images for ESXi and libvirt/qemu/kvm from the base server distribution iso, using [packer](https://www.packer.io/) (and the `vmware-iso` and `qemu` builders).


Several configurations are provided (in `roles/<cloud_type>/templates/<os_id>/`):
+ **ubuntu2404**:  Uses the [autoinstall](https://ubuntu.com/server/docs/install/autoinstall-reference) mechanism
+ **ubuntu2204**:  Uses the [autoinstall](https://ubuntu.com/server/docs/install/autoinstall-reference) mechanism
+ **ubuntu2004**:  Uses the [autoinstall](https://ubuntu.com/server/docs/install/autoinstall-reference) mechanism
+ **ubuntu2004_legacy**:  Uses the legacy preseeding technology.
+ **ubuntu1804**:  Uses the legacy preseeding technology.

## Prerequisites

### libvirt/qemu/kvm config:
+ Because there is no easy-to-use way of connecting to a remote libvirt daemon using username/password, we use Ansible to connect to the libvirt server, and run the provisioning directly.
  + Credentials (username/certificate) should be stored in `group_vars/all/all.yml` in the `image_config.libvirt` dict.
+ Install a vnc viewer.  In Windows WSL2, `sudo apt install tigervnc-viewer` works well.  (Can also use `gvncviewer`, but take care not to connect whilst packer is _typing_ as this takes ownership of the VNC connection and prevents further typing.)
  + Connect to the VNC by `xtigervncviewer -Shared=1 <libvirt_host>:<port or display>`
  + The VNC port is opened to the console whist provisioning is in place. The _display_ number is the last two digits of the VNC port number, so if the port number is _5987_ the display number is _87_ 
  + packer.log in the `/tmp/ansible....` directory will also show the VNC connection string as 0.0.0.0:59xx where xx is the display number.

### ESXI config:
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


### XCP-NG config
+ Not yet functional due to differences in the way packer-plugin-xenserver expects to connect to the image (requires SSH even when communicator is 'none').  See packerlog.txt



## Ansible Vault Secrets
Credentials can be encrypted inline in the playbooks using ansible-vault.  They are exposed to ansible via the `vault_password_file` [script mechanism](https://docs.ansible.com/ansible/latest/user_guide/vault.html#storing-passwords-in-third-party-tools-with-vault-password-client-scripts) (defined to point to `.vaultpass-client.py` in the `ansible.cfg` file), which returns the vault password referenced `VAULT_PASSWORD` environment variable.
```
export VAULT_PASSWORD=<password>
```

## Invocation
```
ansible-playbook gold-img-build.yml -e cloud_type=esxi -e os_id=ubuntu2004 -e uselocal=true
ansible-playbook gold-img-build.yml -e cloud_type=libvirt -e os_id=ubuntu2204 -e uselocal=true
```

### Mandatory command-line variables:
+ `-e cloud_type=<esxi|libvirt|xcp_ng>` - a directory containing cloud templates under `roles/<cloud_type>/templates/<os_id>/`
+ `-e os_id=<ubuntu2004>` - an entry under base_os in `defaults/main.yml`

### Optional extra variables:
+ `-e uselocal=true` - Copies the Ubuntu base image and Packer executable from the local Ansible directory, rather than downloading them. _(default: false)_  
+ `-e use_docker=true` - Run within a Docker container rather than locally. _(default: false)_.

### Test
If the script fails, there will be a remnant in a `/tmp/ansible.[hash]` directory.  Enter this directory, and run:

#### Windows
```
$env:PACKER_LOG=1
$env:PACKER_LOG_PATH="packerlog.txt"
.\packer.exe build -on-error=abort <cloud_type>__<os_id>/packer.json
```
#### Linux
```
export PACKER_LOG=1
export PACKER_LOG_PATH="./packerlog.txt"
./packer build -on-error=abort <cloud_type>__<os_id>/packer.json
```
