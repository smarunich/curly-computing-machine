# curly-computing-machine - NSX Advanced Load Balancer by Avi Networks on top of vSphere using Terraform + Ansible

## Overview

Extensible deployment framework starting from the infrastructure layer covered by Terraform up to the configuration management handled by Ansible.

The current repository deploys n-number of target K8S pods with VMware NSX Advanced Load Balancer (Avi Networks) as Ingress Controller on top of vSphere leveraging [AKO (Avi Kubernetes Operator)](https://avinetworks.com/docs/ako/ako-installation/) .

## Topology

![Topology](curly-computing-machine.png)

### Kubernetes Deployments are reachable via Node Port, LoadBalancer and Ingress objects

LoadBalancer, Ingress are also provided leveraging NSX Advanced Load Balancer and AKO.

| Application Name | Node Port | Description |
| -------- | -------- | -------- |
| kuard     | HTTP/30000     | https://github.com/kubernetes-up-and-running/kuard |
| avinetworks     | HTTP/30001     | https://hub.docker.com/r/smarunich/avinetworks-demo |
| httpbin     | HTTP/30002     | https://httpbin.org/ |
| juice     | HTTP/30003     | https://owasp.org/www-project-juice-shop/ |
| sock-shop     | HTTP/30004     | https://github.com/microservices-demo/microservices-demo |
| kubernetes-dashboard    | HTTP2/30005     | https://github.com/kubernetes/dashboard |
| hackazon    | HTTP/30080, HTTPS/30443     | https://github.com/rapid7/hackazon |
| dvwa    | HTTP/30081     | http://www.dvwa.co.uk/ |

## Requirements
* Terraform 0.12.10 or later
* Ansible 2.6 or later
* vCenter Server vSphere 6.5 or later
* Ubuntu Bionic Template as part of vCenter. Ubuntu VM template has to support user-data, please download official Ubuntu OVA image from https://cloud-images.ubuntu.com/bionic/current/
* Avi Controller Template 18.2.6 or later as part of vCenter.
* DHCP is required for Management Port Group to bootstrap the virtual machines as well as Internet connectivity


## Getting Started
   
   **NOTE**: all the deployment work is suggested to be performed within avitools container: [https://github.com/avinetworks/avitools](https://github.com/avinetworks/avitools)


 1. Clone the repository [https://github.com/smarunich/curly-computing-machine](https://github.com/smarunich/curly-computing-machine)

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
...
ubuntu@jumpbox:~$ ssh master1.pod1.lab
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-96-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Thu Apr 30 20:11:26 UTC 2020

  System load:  0.23              Users logged in:        0
  Usage of /:   5.9% of 57.98GB   IP address for ens192:  10.206.42.223
  Memory usage: 23%               IP address for docker0: 172.17.0.1
  Swap usage:   0%                IP address for cni0:    10.244.0.1
  Processes:    138


18 packages can be updated.
10 updates are security updates.


Last login: Thu Apr 30 18:32:18 2020 from 10.206.42.231
ubuntu@master1:~$ kubectl get nodes -o wide
NAME               STATUS   ROLES    AGE    VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
master1.pod1.lab   Ready    master   123m   v1.18.2   10.206.42.223   <none>        Ubuntu 18.04.4 LTS   4.15.0-96-generic   docker://19.3.6
server1.pod1.lab   Ready    <none>   122m   v1.18.2   10.206.42.212   <none>        Ubuntu 18.04.4 LTS   4.15.0-96-generic   docker://19.3.6
server2.pod1.lab   Ready    <none>   122m   v1.18.2   10.206.42.217   <none>        Ubuntu 18.04.4 LTS   4.15.0-96-generic   docker://19.3.6
server3.pod1.lab   Ready    <none>   122m   v1.18.2   10.206.42.218   <none>        Ubuntu 18.04.4 LTS   4.15.0-96-generic   docker://19.3.6
ubuntu@master1:~$ kubectl get svc -A
NAMESPACE              NAME                        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
default                avinetworks                 NodePort    10.100.236.11    <none>        80:30001/TCP                 123m
default                dvwa                        NodePort    10.110.199.5     <none>        80:30081/TCP                 123m
default                hackazon                    NodePort    10.111.212.244   <none>        80:30080/TCP,443:30443/TCP   123m
default                httpbin                     NodePort    10.100.134.178   <none>        80:30002/TCP                 123m
default                juice                       NodePort    10.96.25.182     <none>        3000:30003/TCP               123m
default                kuard                       NodePort    10.99.5.233      <none>        8080:30000/TCP               123m
default                kubernetes                  ClusterIP   10.96.0.1        <none>        443/TCP                      123m
kube-system            kube-dns                    ClusterIP   10.96.0.10       <none>        53/UDP,53/TCP,9153/TCP       123m
kubernetes-dashboard   dashboard-metrics-scraper   ClusterIP   10.104.57.68     <none>        8000/TCP                     123m
kubernetes-dashboard   kubernetes-dashboard        NodePort    10.100.228.249   <none>        8443:30005/TCP               123m
sock-shop              carts                       ClusterIP   10.101.42.65     <none>        80/TCP                       123m
sock-shop              carts-db                    ClusterIP   10.105.227.49    <none>        27017/TCP                    123m
sock-shop              catalogue                   ClusterIP   10.96.204.146    <none>        80/TCP                       123m
sock-shop              catalogue-db                ClusterIP   10.111.104.99    <none>        3306/TCP                     123m
sock-shop              front-end                   NodePort    10.104.217.196   <none>        80:30004/TCP                 123m
sock-shop              orders                      ClusterIP   10.100.180.224   <none>        80/TCP                       123m
sock-shop              orders-db                   ClusterIP   10.107.153.61    <none>        27017/TCP                    123m
sock-shop              payment                     ClusterIP   10.107.94.70     <none>        80/TCP                       123m
sock-shop              queue-master                ClusterIP   10.100.222.80    <none>        80/TCP                       123m
sock-shop              rabbitmq                    ClusterIP   10.102.254.17    <none>        5672/TCP                     123m
sock-shop              shipping                    ClusterIP   10.103.93.89     <none>        80/TCP                       123m
sock-shop              user                        ClusterIP   10.101.204.165   <none>        80/TCP                       123m
sock-shop              user-db                     ClusterIP   10.101.77.230    <none>        27017/TCP                    123m

ubuntu@master1:~$ kubectl describe secret -n kubernetes-dashboard kubernetes-dashboard
```

11. (Optional) Access Kubernetes Dashboard using one of the servers node addresses, https://10.206.42.218:30005 with the secret retrieved from the previous step.
