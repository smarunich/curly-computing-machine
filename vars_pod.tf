#Name of folder to be created, also uniqueness value for disk, etc
variable "id" {
  default     = "pso_enable"
}

#Number of controllers to deploy
variable "pod_count" {
  default     = "1"
}

variable "controller_template" {
  default     = "controller-18.2.6-9134-template"
}

#Controller CPUs
variable "cpu" {
  default = 8
}

#Controller Memory
variable "mem" {
  default = 24768
}

#Variable declaration for OVA parameters
variable "mgmt_ip" {}     
variable "mgmt_mask" {}
variable "default_gw" {}  
