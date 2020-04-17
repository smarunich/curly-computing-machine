
data "template_file" "master_userdata" {
  count    = var.master_count * var.pod_count
  template = file("${path.module}/userdata/master.userdata")

  vars = {
    hostname = "master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab"
    vm_name =  "${var.id}_master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab"
    password          = var.avi_admin_password
    pubkey            = tls_private_key.generated.public_key_openssh
    jumpbox_ip        = vsphere_virtual_machine.jumpbox.default_ip_address
    vcenter_host      = var.vsphere_server
    vcenter_user      = var.vsphere_user
    vcenter_password  = var.vsphere_password
    dns_server        = var.dns_server
    number   = count.index + 1
  }
}

data "vsphere_virtual_machine" "master_template" {
  name          = var.server["template"]
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_tag" "master_name" {
  count            = var.master_count * var.pod_count
  name             = "master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab"
  category_id      = vsphere_tag_category.name.id
}

resource "vsphere_tag" "master_lab_name" {
  count            = var.master_count * var.pod_count
  name             = "master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab"
  category_id      = vsphere_tag_category.lab_name.id
}

resource "vsphere_tag" "k8s_masters_lab_group" {
  name             = "k8s_masters"
  category_id      = vsphere_tag_category.lab_group.id
}

resource "vsphere_virtual_machine" "master" {
  count            = var.master_count * var.pod_count
  name             = "${var.id}_master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab"
  datastore_id     = data.vsphere_datastore.datastore.id
  resource_pool_id = vsphere_resource_pool.resource_pool.id
  folder           = vsphere_folder.folder.path
  network_interface {
                      network_id = data.vsphere_network.network.id
  }

  num_cpus = var.server["cpu"]
  memory = var.server["memory"]
  wait_for_guest_net_timeout = 1
  guest_id = data.vsphere_virtual_machine.master_template.guest_id
  scsi_type = data.vsphere_virtual_machine.master_template.scsi_type
  scsi_bus_sharing = data.vsphere_virtual_machine.master_template.scsi_bus_sharing
  scsi_controller_count = data.vsphere_virtual_machine.master_template.scsi_controller_scan_count

  disk {
    size             = var.server["disk"]
    label            = "${var.id}_master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab_vmdk"
    eagerly_scrub    = data.vsphere_virtual_machine.master_template.disks.0.eagerly_scrub
    thin_provisioned = data.vsphere_virtual_machine.master_template.disks.0.thin_provisioned
  }

  cdrom {
    client_device = true
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.master_template.id
  }

  tags = [
        vsphere_tag.master_name[count.index].id,
        vsphere_tag.master_lab_name[count.index].id,
        vsphere_tag.k8s_masters_lab_group.id,
        vsphere_tag.owner.id,
        vsphere_tag.lab_id.id,

        vsphere_tag.lab_timezone.id
  ]

   vapp {
     properties = {
      hostname    = "master${floor(count.index / var.pod_count % var.master_count + 1)}.pod${count.index % var.pod_count + 1}.lab"
      password    = var.avi_admin_password
      public-keys = tls_private_key.generated.public_key_openssh
      user-data   = base64encode(data.template_file.master_userdata[count.index].rendered)
    }
  }

  depends_on        = [ vsphere_virtual_machine.jumpbox ]

}
