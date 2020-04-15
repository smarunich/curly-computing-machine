#!/usr/bin/env python3
import requests
import datetime
import json
import sys
import redis
import os
from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim, VmomiSupport
from requests.auth import HTTPBasicAuth

def touch(fname):
    with open(fname, 'a'):
        os.utime(fname, None)

def get_object_by_name(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    return obj

def get_vm_id_by_name(si, vm_name):
    content = si.RetrieveContent()
    vm = get_object_by_name(content, [vim.VirtualMachine], vm_name)
    vm_id = str(vm).split(':')[1].replace('\'','')
    return vm_id

def get_vm_metadata(si, vm_name):
    vm_id = get_vm_id_by_name(si, vm_name)
    obj = VmomiSupport.templateOf("VirtualMachine")(vm_id, si._stub)
    obj_metadata = json.loads(json.dumps(obj, cls=VmomiSupport.VmomiJSONEncoder))
    return obj_metadata['guest']

blocker_fname = "/opt/register_blocker"
exists = os.path.isfile(blocker_fname)

if not exists:
    redis_host = sys.argv[1]
    vcenter_host = sys.argv[2]
    vcenter_user = sys.argv[3]
    vcenter_password = sys.argv[4]
    vm_name = sys.argv[5]
    si = SmartConnectNoSSL(host=vcenter_host,
                            user=vcenter_user,
                            pwd=vcenter_password)
    identity = get_vm_metadata(si, vm_name)
    vm_id = get_vm_id_by_name(si, vm_name)
    identity['vmId'] = vm_id
    identity['now'] = datetime.datetime.now().isoformat()
    identity['localhostname'] = os.uname()[1]
    identity['network'] = identity['net'][0]['network']
    identity.pop('net')
    identity.pop('ipStack')
    identity.pop('disk')
    identity.pop('screen')
    # Serialize the tags
    vcenter_url = "https://" + vcenter_host + "/rest"
    vcenter_url_auth = vcenter_url + "/com/vmware/cis/session"
    resp = requests.post(
        vcenter_url_auth,
        auth=HTTPBasicAuth(vcenter_user, vcenter_password),
        verify=False
    )
    session_id = resp.json()['value']
    vcenter_url_vm_list_attached_tags = vcenter_url + "/com/vmware/cis/tagging/tag-association?~action=list-attached-tags"
    vm_obj = {"object_id": {"id": vm_id, "type": "VirtualMachine"}}
    resp = requests.post(
        vcenter_url_vm_list_attached_tags, data=json.dumps(vm_obj),
        headers={
            'vmware-api-session-id': session_id,
            'content-type': 'application/json'
        },
        verify=False
    )
    tags = resp.json()['value']
    vcenter_url_get_tag = vcenter_url + "/com/vmware/cis/tagging/tag/id:{}"
    vcenter_url_get_category = vcenter_url + "/com/vmware/cis/tagging/category/id:{}"
    for tag in tags:
        resp = requests.get(
                vcenter_url_get_tag.format(tag),
                headers={'vmware-api-session-id': session_id},
                verify=False
        )
        tag_value = resp.json()['value']['name']
        category_id = resp.json()['value']['category_id']
        resp = requests.get(
                vcenter_url_get_category.format(category_id),
                headers={'vmware-api-session-id': session_id},
                verify=False
        )
        tag_name = resp.json()['value']['name']
        identity[tag_name] = tag_value
    report = { identity['vmId']: identity }
    r = redis.client.StrictRedis(host=redis_host, port=6379, db=0)
    r.publish('instances', json.dumps(report))
    touch(blocker_fname)