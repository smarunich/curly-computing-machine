
data "vsphere_virtual_machine" "controller_template" {
  name          = var.controller["template"]
  datacenter_id = data.vsphere_datacenter.dc.id
}


resource "vsphere_tag" "controller_name" {
  count            = var.pod_count
  name             = "controller.pod${count.index + 1}.lab"
  category_id      = vsphere_tag_category.name.id
}

resource "vsphere_tag" "controller_lab_name" {
  count            = var.pod_count
  name             = "controller.pod${count.index + 1}.lab"
  category_id      = vsphere_tag_category.lab_name.id
}

resource "vsphere_tag" "controller_lab_group" {
  name             = "controllers"
  category_id      = vsphere_tag_category.lab_group.id
}

resource "vsphere_virtual_machine" "controller" {
  count            = var.pod_count
  name             = "${var.id}_controller.pod${count.index + 1}.lab"
  datastore_id     = data.vsphere_datastore.datastore.id
  resource_pool_id = data.vsphere_resource_pool.pool.id
  folder           = vsphere_folder.folder.path
  network_interface {
    network_id = data.vsphere_network.network.id
  }

  num_cpus = var.controller["cpu"]
  memory = var.controller["memory"]

  guest_id = data.vsphere_virtual_machine.controller_template.guest_id
  scsi_type = data.vsphere_virtual_machine.controller_template.scsi_type
  scsi_bus_sharing = data.vsphere_virtual_machine.controller_template.scsi_bus_sharing
  scsi_controller_count = data.vsphere_virtual_machine.controller_template.scsi_controller_scan_count

  disk {
    size             = var.controller["disk"]
    label            = "${var.id}_controller.pod${count.index + 1}.${var.id}.lab_vmdk"
    eagerly_scrub    = data.vsphere_virtual_machine.controller_template.disks.0.eagerly_scrub
    thin_provisioned = data.vsphere_virtual_machine.controller_template.disks.0.thin_provisioned
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.controller_template.id
  }

  tags = [
        vsphere_tag.controller_name[count.index].id,
        vsphere_tag.controller_lab_name[count.index].id,
        vsphere_tag.controller_lab_group.id,
        vsphere_tag.owner.id,
        vsphere_tag.lab_id.id,
        vsphere_tag.lab_timezone.id
  ]

   vapp {
     properties = {
  #    "mgmt-ip"     = var.controller["mgmt_ip"]
  #    "mgmt-mask"   = var.controller["mgmt_mask"]
  #    "default-gw"  = var.controller["default_gw"]
      sysadmin-public-key = tls_private_key.generated.public_key_openssh
    }
  }

}
