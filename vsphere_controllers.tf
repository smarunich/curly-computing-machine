
data "vsphere_virtual_machine" "controller_template" {
  name          = var.controller_template
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_virtual_machine" "controller" {
  count            = var.pod_count
  name             = "${var.id}_podt${count.index + 1}_controller"
  datastore_id     = data.vsphere_datastore.datastore.id
  resource_pool_id = data.vsphere_resource_pool.pool.id
  folder           = vsphere_folder.folder.path
  network_interface {
    network_id = data.vsphere_network.network.id
  }

  num_cpus = var.cpu
  memory = var.mem
  guest_id = data.vsphere_virtual_machine.controller_template.guest_id
  scsi_type = data.vsphere_virtual_machine.controller_template.scsi_type
  scsi_bus_sharing = data.vsphere_virtual_machine.controller_template.scsi_bus_sharing
  scsi_controller_count = data.vsphere_virtual_machine.controller_template.scsi_controller_scan_count

  disk {
    label           = "${var.id}_podt${count.index + 1}_controller.vmdk"
    eagerly_scrub    = data.vsphere_virtual_machine.controller_template.disks.0.eagerly_scrub
    size             = data.vsphere_virtual_machine.controller_template.disks.0.size
    thin_provisioned = data.vsphere_virtual_machine.controller_template.disks.0.thin_provisioned
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.controller_template.id
  }

  vapp {
    properties = {
      "mgmt-ip"                        = var.mgmt_ip
      "mgmt-mask"                = var.mgmt_mask      
      "default-gw"        = var.default_gw   
    }
  }
}