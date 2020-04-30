data "vsphere_datacenter" "dc" {
  name = var.dc
}

data "vsphere_compute_cluster" "compute_cluster" {
  name          = var.cluster
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_datastore" "datastore" {
  name = var.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_resource_pool" "resource_pool" {
  name                    = var.id
  parent_resource_pool_id = data.vsphere_compute_cluster.compute_cluster.resource_pool_id
}

data "vsphere_network" "network" {
  name = var.network
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_folder" "folder" {
  path          = var.id
  type          = "vm"
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_tag_category" "name" {
  name = "Name"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "owner" {
  name = "Owner"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_group" {
  name = "Lab_Group"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_name" {
  name = "Lab_Name"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_id" {
  name = "Lab_Id"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_avi_default_password" {
  name = "Lab_avi_default_password"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_avi_admin_password" {
  name = "Lab_avi_admin_password"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_avi_backup_admin_username" {
  name = "Lab_avi_backup_admin_username"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_avi_backup_admin_password" {
  name = "Lab_avi_backup_admin_password"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_timezone" {
  name = "Lab_Timezone"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_vcenter_host" {
  name = "Lab_vcenter_host"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}


resource "vsphere_tag_category" "lab_vcenter_user" {
  name = "Lab_vcenter_user"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_vcenter_password" {
  name = "Lab_vcenter_id"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_dc" {
  name = "Lab_dc"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_dns_server" {
  name = "Lab_dns_server"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "lab_vip_ipam_cidr" {
  name = "Lab_vip_ipam_cidr"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}

resource "vsphere_tag_category" "ansible_connection" {
  name = "ansible_connection"
  cardinality = "SINGLE"
  associable_types = [
    "VirtualMachine",
  ]
}


resource "vsphere_tag" "owner" {
  name             = var.owner
  category_id      = vsphere_tag_category.owner.id
}

resource "vsphere_tag" "lab_id" {
  name             = var.id
  category_id      = vsphere_tag_category.lab_id.id
}

resource "vsphere_tag" "lab_timezone" {
  name             = var.lab_timezone
  category_id      = vsphere_tag_category.lab_timezone.id
}

resource "vsphere_tag" "ansible_connection_local" {
  name             = "local"
  category_id      = vsphere_tag_category.ansible_connection.id
}