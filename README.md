# curly-computing-machine

## Solution Overview

Extensible deployment framework starting from the infrastructure layer covered by Terraform up to the configuration management handled by Ansible.

The current repo deploys n-number of target K8S pods with VMware NSX Advanced Load Balancer (Avi Networks) as Ingress Controller on top of vSphere.

## Topology

![Topology](curly-computing-machine.png)

### Applications

Applications available via Node Ports on Servers. Ingress automation is available optionally.

  - KUARD - Port 30000
  - avinetworks - Port 30001
  - httpbin - Port 30002
  - juice - Port 30003
  - sock-shop - Port 30004
  - hackazon - Port 30080, Port 30443 (SSL)
  - kubernetes-dashboard - Port 30005
  - dvwa - Port 30081
  - jupyter - Port 30082

## Requirements

 - Terraform >= 0.12.10
 - Ansible >= 2.9.2
 - vCenter (tested starting 6.5+)
 - Ubuntu OVA image imported as VM template. Ubuntu VM template has to support user-data, please download official Ubuntu OVA image from https://cloud-images.ubuntu.com/bionic/current/
 - Avi Controller image (18.2.6+) imported as VM template
 - DHCP is required for Management Port Group to bootstrap the virtual machines as well as Internet connectivity

     **NOTE**: all the deployment work was performed within avitools container: [https://github.com/avinetworks/avitools](https://github.com/avinetworks/avitools)

## Getting Started

      **NOTE**: all the deployment work was performed within avitools container: [https://github.com/avinetworks/avitools](https://github.com/avinetworks/avitools)

 1. Clone the repository - [https://github.com/smarunich/curly-computing-machine](https://github.com/smarunich/curly-computing-machine)

```
root@avitools:~# git clone https://github.com/smarunich/curly-computing-machine
Cloning into ‘curly-computing-machine'...
```

 2. Initialize a Terraform working directory
 ```
root@avitools:~/curly-computing-machine# terraform init
Initializing the
backend... Initializing provider plugins... Checking for available
provider plugins...

* provider.local: version = "~> 1.4"
* provider.random: version = "~> 2.2"
* provider.template: version = "~> 2.1"
* provider.tls: version = "~> 2.1"
* provider.vsphere: version = "~> 1.17"

Terraform has been successfully initialized!
```
3. Copy the minimum required variables template
```
root@avitools:~/curly-computing-machine# cp sample_terraform_tfvars terraform.tfvars
```
4. Fill out the required variables - terraform.tfvars

```
#terraform.tfvars
vsphere_server = ""
vsphere_user = ""
vsphere_password = ""
avi_admin_password = "AviNetworks123!"
avi_default_password = "58NFaGDJm(PJH0G"
avi_backup_admin_username = "aviadmin"
avi_backup_admin_password = "AviNetworks123!"
pod_count = 2
id = "magicenable"
dns_server = ""
dc = "dc01"
cluster = "cluster01"
datastore = "vsan"
network = "pg-mgmt"
vip_ipam_cidr = "10.206.40.0/22"
vip_ipam_allocation_range = "10.206.41.1-10.206.41.40"
```
5. Update vars_pod.tf with appropriate VM template names for jumpbox, server and controller objects
```
variable "controller" {
  type = map
  default = {
    cpu = 8
    memory = 24768
    disk = 128
    template = "controller-18.2.6-9134-template"
  # mgmt_ip = ""
  # mgmt_mask = ""
  # default_gw = ""
  }
}

variable "jumpbox" {
  type = map
  default = {
    cpu = 2
    memory = 4096
    disk = 20
    # The image must support user-data, https://cloud-images.ubuntu.com/bionic/current/
    template = "ubuntu-bionic-18.04-cloudimg-20200407"
  # mgmt_ip = ""
  # mgmt_mask = ""
  # default_gw = ""
  }
}

variable "server" {
  type = map
  default = {
    cpu = 2
    memory = 4096
    disk = 60
    # The image must support user-data, https://cloud-images.ubuntu.com/bionic/current/
    template = "ubuntu-bionic-18.04-cloudimg-20200407"
  # mgmt_ip = ""
  # mgmt_mask = ""
  # default_gw = ""
  }
```
6. Prepare the terraform plan
```
root@avitools:~/curly-computing-machine# terraform plan

…

Plan: 74 to add, 0 to change, 0 to destroy.
------------------------------------------------------------------------
Note: You didn't specify an "-out" parameter to save this plan, so
Terraform can't guarantee that exactly these actions will be performed
if "terraform apply" is subsequently run
7. Apply the terraform plan
aviadmin@avitools:~/curly-computing-machine# terraform apply

…
Plan: 74 to add, 0 to change, 0 to destroy.
Do you want to perform these actions?   Terraform will perform the
actions described above.   Only 'yes' will be accepted to approve.

Enter a value: yes

...

Apply complete! Resources: 40 added, 0 changed, 0 destroyed.

Outputs:
controllers = [
  "10.206.42.224",
  "10.206.42.230",
]
jumpbox = 10.206.42.231
masters = [
  "10.206.42.223",
  "10.206.42.222",
]
```
9. SSH into the environment
```
 aviadmin@avitools:~/curly-computing-machine# ls keys/
generated-access-key-kid.pem  generated-access-key-kid.pub
 aviadmin@avitools:~/curly-computing-machine# ssh -i keys/generated-access-key-kid.pem 10.206.42.231 -l ubuntu
 ```
10. (Optional) Check the registered inventory
```
ubuntu@jumpbox:~$ cat /etc/hosts
127.0.0.1	localhost
fe00::0	ip6-localnet
ff00::0	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
ff02::3	ip6-allhosts
10.206.42.231	jumpbox.pod.lab
10.206.42.230	controller.pod2.lab
10.206.42.224	controller.pod1.lab
10.206.42.222	master1.pod2.lab
10.206.42.223	master1.pod1.lab
10.206.42.219	server1.pod2.lab
10.206.42.216	server2.pod2.lab
10.206.42.218	server3.pod1.lab
10.206.42.217	server2.pod1.lab
10.206.42.212	server1.pod1.lab
10.206.42.209	server3.pod2.lab

ubuntu@jumpbox:~$ /etc/ansible/hosts --list | jq . | more
{
  "_meta": {
    "hostvars": {
      "controller.pod2.lab": {
        "dynamicType": "None",
        "dynamicProperty": "[]",
        "toolsStatus": "toolsOk",
        "toolsVersionStatus": "guestToolsUnmanaged",
        "toolsVersionStatus2": "guestToolsUnmanaged",
        "toolsRunningStatus": "guestToolsRunning",
        "toolsVersion": "10304",
        "toolsInstallType": "guestToolsTypeOpenVMTools",
        "guestId": "ubuntu64Guest",
        "guestFamily": "linuxGuest",
        "guestFullName": "Ubuntu Linux (64-bit)",
        "hostName": "Avi-Controller",
        "ipAddress": "10.206.42.230",
        "guestState": "running",
        "appHeartbeatStatus": "appStatusGray",
        "guestKernelCrashed": "False",
        "appState": "none",
        "guestOperationsReady": "True",
        "interactiveGuestOperationsReady": "False",
        "guestStateChangeSupported": "True",
        "generationInfo": "[]",
        "hwVersion": "None",
        "_vimtype": "vim.vm.GuestInfo",
        "vmId": "vm-1751",
        "now": "2020-04-30T18:06:01.474731",
        "localhostname": "jumpbox.pod.lab",
        "network": "vxw-dvs-34-virtualwire-3-sid-6100002-wdc-06-vc10-avi-mgmt",
        "Lab_Timezone": "EST",
        "ansible_connection": "local",
        "Lab_Group": "controllers",
        "Lab_Id": "enable",
        "Lab_Name": "controller.pod2.lab",
        "Owner": "aviVMware_Training",
        "Name": "controller.pod2.lab"
      },
```
