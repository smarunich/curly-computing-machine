variable "vsphere_user" {
}

variable "vsphere_password" {
}

variable "vsphere_server" {
}


variable "dc" {
  default     = "wdc-06-vc10"
}

variable "compute_cluster" {
  default     = "wdc-06-vc10c01"
}

variable "datastore" {
  default     = "wdc-06-vc10c01-vsan"
}

variable "network" {
  default     = "vxw-dvs-34-virtualwire-3-sid-6100002-wdc-06-vc10-avi-mgmt"
}
