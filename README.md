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

     **NOTE**: all the deployment work was performed within avitools container: [https://github.com/avinetworks/avitools](https://github.com/avinetworks/avitools)

## Getting Started
