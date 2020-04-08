data "vsphere_datacenter" "dc" {
  name = var.dc
}

data "vsphere_compute_cluster" "compute_cluster" {
  name          = var.compute_cluster
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_datastore" "datastore" {
  name = var.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name = var.network
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_resource_pool" "pool" {
  name          = "Resources"
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
