variable "vsphere_user" {
}

variable "vsphere_password" {
}

variable "vsphere_server" {
}

variable "dns_server" {
  default = "8.8.8.8"
}

variable "dc" {
  default     = "wdc-06-vc10"
}

variable "cluster" {
  default     = "wdc-06-vc10c01"
}

variable "datastore" {
  default     = "wdc-06-vc10c01-vsan"
}

variable "network" {
  default     = "vxw-dvs-34-virtualwire-3-sid-6100002-wdc-06-vc10-avi-mgmt"
}
