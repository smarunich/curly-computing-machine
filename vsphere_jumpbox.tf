
data "template_file" "jumpbox_userdata" {
  template = file("${path.module}/userdata/jumpbox.userdata")
  vars = {
    hostname     = "jumpbox.pod.lab"
    password     = var.avi_admin_password
    pkey         = tls_private_key.generated.private_key_pem
    pubkey       = tls_private_key.generated.public_key_openssh
    vcenter_host      = var.vsphere_server
    vcenter_user      = var.vsphere_user
    vcenter_password  = var.vsphere_password
    projectid = var.id
  }
}

data "vsphere_virtual_machine" "jumpbox_template" {
  name          = var.jumpbox["template"]
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_tag" "jumpbox_name" {
  name             = "jumpbox.pod.lab"
  category_id      = vsphere_tag_category.name.id
}

resource "vsphere_tag" "jumpbox_lab_name" {
  name             = "jumpbox.pod.lab"
  category_id      = vsphere_tag_category.lab_name.id
}

resource "vsphere_tag" "jumpbox_lab_group" {
  name             = "jumpbox"
  category_id      = vsphere_tag_category.lab_group.id
}

resource "vsphere_tag" "lab_avi_default_password" {
  name             = var.avi_default_password
  category_id      = vsphere_tag_category.lab_avi_default_password.id
}

resource "vsphere_tag" "lab_avi_admin_password" {
  name             = var.avi_admin_password
  category_id      = vsphere_tag_category.lab_avi_admin_password.id
}

resource "vsphere_tag" "lab_avi_backup_admin_username" {
  name             = var.avi_backup_admin_username
  category_id      = vsphere_tag_category.lab_avi_backup_admin_username.id
}

resource "vsphere_tag" "lab_avi_backup_admin_password" {
  name             = var.avi_backup_admin_password
  category_id      = vsphere_tag_category.lab_avi_backup_admin_password.id
}

resource "vsphere_tag" "lab_dc" {
  name             = var.dc
  category_id      = vsphere_tag_category.lab_dc.id
}

resource "vsphere_tag" "lab_vcenter_host" {
  name             = var.vsphere_server
  category_id      = vsphere_tag_category.lab_vcenter_host.id
}

resource "vsphere_tag" "lab_vcenter_user" {
  name             = var.vsphere_user
  category_id      = vsphere_tag_category.lab_vcenter_user.id
}

resource "vsphere_tag" "lab_vcenter_password" {
  name             = base64encode(var.vsphere_password)
  category_id      = vsphere_tag_category.lab_vcenter_password.id
}

resource "vsphere_tag" "lab_dns_server" {
  name             = var.dns_server
  category_id      = vsphere_tag_category.lab_dns_server.id
}

resource "vsphere_tag" "lab_vip_ipam_cidr" {
  name             = var.vip_ipam_cidr
  category_id      = vsphere_tag_category.lab_vip_ipam_cidr.id
}

resource "vsphere_virtual_machine" "jumpbox" {
  name             = "${var.id}_jumpbox.pod.lab"
  datastore_id     = data.vsphere_datastore.datastore.id
  resource_pool_id = vsphere_resource_pool.resource_pool.id
  folder           = vsphere_folder.folder.path
  network_interface {
                      network_id = data.vsphere_network.network.id
  }

  num_cpus = var.jumpbox["cpu"]
  memory = var.jumpbox["memory"]
  wait_for_guest_net_timeout = var.wait_for_guest_net_timeout
  guest_id = data.vsphere_virtual_machine.jumpbox_template.guest_id
  scsi_type = data.vsphere_virtual_machine.jumpbox_template.scsi_type
  scsi_bus_sharing = data.vsphere_virtual_machine.jumpbox_template.scsi_bus_sharing
  scsi_controller_count = data.vsphere_virtual_machine.jumpbox_template.scsi_controller_scan_count

  disk {
    size             = var.jumpbox["disk"]
    label            = "${var.id}_jumpbox.pod.lab_vmdk"
    eagerly_scrub    = data.vsphere_virtual_machine.jumpbox_template.disks.0.eagerly_scrub
    thin_provisioned = data.vsphere_virtual_machine.jumpbox_template.disks.0.thin_provisioned
  }

  cdrom {
    client_device = true
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.jumpbox_template.id
  }

  tags = [
        vsphere_tag.jumpbox_name.id,
        vsphere_tag.jumpbox_lab_name.id,
        vsphere_tag.jumpbox_lab_group.id,
        vsphere_tag.owner.id,
        vsphere_tag.lab_id.id,
        vsphere_tag.network.id,

        vsphere_tag.lab_avi_default_password.id,
        vsphere_tag.lab_avi_admin_password.id,
        vsphere_tag.lab_avi_backup_admin_username.id,
        vsphere_tag.lab_avi_backup_admin_password.id,

        vsphere_tag.lab_dc.id,
        vsphere_tag.lab_vcenter_host.id,
        vsphere_tag.lab_vcenter_user.id,
        vsphere_tag.lab_vcenter_password.id,

        vsphere_tag.lab_dns_server.id,
        vsphere_tag.lab_vip_ipam_cidr.id,

        vsphere_tag.lab_timezone.id
  ]

   vapp {
     properties = {
      hostname    = "jumpbox"
      password    = var.avi_admin_password
      public-keys = tls_private_key.generated.public_key_openssh
      user-data   = base64encode(data.template_file.jumpbox_userdata.rendered)
    }
  }

  connection {
    host        = self.default_ip_address
    type        = "ssh"
    agent       = false
    user        = "ubuntu"
    private_key = tls_private_key.generated.private_key_pem
  }

  provisioner "remote-exec" {
    inline      = [
      "while [ ! -f /tmp/cloud-init.done ]; do sleep 1; done"
    ]
  }

  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i '${vsphere_virtual_machine.jumpbox.default_ip_address},' --private-key ${local.private_key_filename} -e'private_key_filename=${local.private_key_filename} vcenter_host=${var.vsphere_server} vcenter_user=${var.vsphere_user} vcenter_password=${var.vsphere_password} vm_name=${var.id}_jumpbox.pod.lab dns_server=${var.dns_server} vip_ipam_cidr=${var.vip_ipam_cidr} vip_ipam_allocation_range=${var.vip_ipam_allocation_range}' -e 'ansible_python_interpreter=/usr/bin/python3' --user ubuntu provisioning/provision_jumpbox.yml"
  }

}
