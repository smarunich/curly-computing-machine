#Name of folder to be created, also uniqueness value for disk, etc
variable "id" {
  default     = "aviVMware"
}

variable "owner" {
  description = "Sets the AWS Owner tag appropriately"
  default     = "aviVMware_Training"
}
#Number of controllers to deploy
variable "pod_count" {
  default     = "1"
}

variable "master_count" {
  description = "K8S Masters count per pod"
  default     = "1"
}

variable "server_count" {
  description = "K8S Workers count per pod"
  default     = "3"
}

#Controller Details
variable "controller" {
  type = map
  default = {
    cpu = 8
    memory = 24768
    disk = 128
    template = "controller-18.2.8-9205-template"
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
}


variable "avi_default_password" {
}

variable "avi_admin_password" {
}

variable "avi_backup_admin_username" {
}

variable "avi_backup_admin_password" {
}

variable "lab_timezone" {
  description = "Lab Timezone: PST, EST, GMT or SGT"
  default = "EST"
}

# depends on the underlay lab environment, it can take longer than 2 minutes for VM to come up and get IP address by DHCP
variable "wait_for_guest_net_timeout" {
  default = "5"
}

variable "vip_ipam_cidr" {
 default = "10.206.40.0/22"
}

variable "vip_ipam_allocation_range" {
 default = "10.206.41.1-10.206.41.40"
}
