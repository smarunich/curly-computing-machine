#!/usr/bin/env python3
import requests
import datetime
import json
import sys
import redis
from time import sleep
import os, logging
import psutil
import signal
from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim, VmomiSupport
from datetime import datetime, timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class identity(object):
    def __init__(self, document=None):
        if document is None:
            # need to follow register.py process for data retrieval
            document = {}
        else:
            identity = document
        for k, v in identity.items():
            if isinstance(k, str):
                setattr(self, k, v)
            else:
                setattr(self, k.decode('utf-8'), v)

    def _get_url(self, url):
        response = requests.get(url)
        try:
            response.raise_for_status()
        except:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    def __call__(self):
        return self.__dict__

class hosts_file(object):
    def __init__(self, ip_address, hostname, filename='/etc/hosts'):
        hosts = {}
        found = False
        with open(filename) as fh:
            original_hosts = fh.readlines()
        for line in original_hosts:
            try:
                (ip, name) = line.split()
                if hostname == name:
                    hosts[name] = ip_address
                else:
                    hosts[name] = ip
            except ValueError as err:
                pass
        if not found:
            hosts[hostname] = ip_address
        with open(filename, 'w') as fh:
            for k in hosts.keys():
                if isinstance(k, bytes):
                    k = k.decode()
                print('%s\t%s' % (hosts[k], k), file=fh)
        for pid in psutil.process_iter(['pid', 'name']):
            if pid.info['name'] == "dnsmasq":
                os.kill(pid.info['pid'], signal.SIGHUP)
                break

class vcenter_inventory():
    def __init__(self, session, event, vcenter_server):
        self.vcenter_server = vcenter_server
        self.vm_id = str(event.vm.vm).split(':')[1].replace('\'','')
        self.session = session
        self.identity = {}
        self.vcenter_url = 'https://' + self.vcenter_server + '/rest'
        self.session.post(self.vcenter_url + '/com/vmware/cis/session')

    def collect(self):
        network_check = self._vm_get('/guest/identity')
        status = network_check.status_code
        while status != 200:
            network_check = self._vm_get('/guest/identity')
            status = network_check.status_code
        self.identity.update(network_check.json()['value'])
        self.identity['vmId'] = self.vm_id
        self.identity['now'] = datetime.now().isoformat()
        self.tag_parse()
        return(self.identity)
    
    def _vm_get(self, api_path):
        resp = self.session.get('https://' + self.vcenter_server + '/rest/vcenter/vm/' + self.vm_id  + api_path)
        return(resp)

    #tag serialization
    def tag_parse(self):
        vcenter_url_vm_list_attached_tags = self.vcenter_url + "/com/vmware/cis/tagging/tag-association?~action=list-attached-tags"
        vm_obj = {"object_id": {"id": self.vm_id, "type": "VirtualMachine"}}
        resp = self.session.post(vcenter_url_vm_list_attached_tags, data=json.dumps(vm_obj),
                headers={
                    'content-type': 'application/json'
                })
        tags = resp.json()['value']
        vcenter_url_get_tag = self.vcenter_url + "/com/vmware/cis/tagging/tag/id:{}"
        vcenter_url_get_category = self.vcenter_url + "/com/vmware/cis/tagging/category/id:{}"
        for tag in tags:
            resp = self.session.get(vcenter_url_get_tag.format(tag))
            tag_value = resp.json()['value']['name']
            category_id = resp.json()['value']['category_id']
            resp = self.session.get(
                    vcenter_url_get_category.format(category_id))
            tag_name = resp.json()['value']['name']
            self.identity[tag_name] = tag_value

class redis_inventory():
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def update_redis(self,id):
        self.identity = identity(id)
        old_identity = self.redis.hgetall(self.identity.Name)
        if old_identity:
            self.old_identity = identity(document=old_identity)
            self.redis.srem(self.old_identity.Lab_Group, self.old_identity.ip_address)
        self.redis.hmset(self.identity.Name, self.identity())
        self.redis.sadd(self.identity.Lab_Group, self.identity.ip_address)
        self.redis.sadd('groups', self.identity.Lab_Group)
        self.redis.sadd('names', self.identity.Name)

    def check_redis(self, vm_hostname):
        return(self.redis.hgetall(vm_hostname))
    
    def publish_redis(self,channel,pdata):
        self.redis.publish(channel,json.dumps({'bootstrap':pdata}))

#global vars
interval = 25
last_event_key = 0

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#host vars
vcenter_host = sys.argv[1]
vcenter_user = sys.argv[2]
vcenter_password = sys.argv[3]
id_name = sys.argv[4]
client = SmartConnectNoSSL(host=vcenter_host,
                        user=vcenter_user,
                        pwd=vcenter_password)

#event collection vars
time_filter = vim.event.EventFilterSpec.ByTime()
event_type_list = ['VmPoweredOnEvent','DrsVmPoweredOnEvent']

#requests session vars
session = requests.Session()
session.verify = False
session.auth = (vcenter_user,vcenter_password)

host_inv = redis_inventory()

try:
    while True:
        #query within updated timeframe
        current = client.CurrentTime()
        now = current.replace(tzinfo=None)
        time_filter.beginTime = now - timedelta(minutes=30)
        time_filter.endTime = now
        filter_spec = vim.event.EventFilterSpec(eventTypeId=event_type_list,time=time_filter)
        collect_events  = client.content.eventManager.CreateCollectorForEvents(filter=filter_spec)

        #loop through events
        for event in reversed(collect_events.latestPage):
            if last_event_key < event.key:
                login = vcenter_inventory(session,event,vcenter_host)
                check_vm_power = login._vm_get('/power')
                if check_vm_power.status_code == 200 and check_vm_power.json()['value']['state'] == "POWERED_ON":
                    log.debug('handle_register detects Power on Event for' + event.vm.name)
                    inv_collection = login.collect()
                    in_redis = host_inv.check_redis(inv_collection['host_name'])
                    #execute when host not found in redis
                    if not bool(in_redis):
                        log.debug('handle_register adding vm' + inv_collection['host_name'])
                        hosts_file(inv_collection['ip_address'], inv_collection['Lab_Name'])
                        host_inv.update_redis(inv_collection)
                        host_inv.publish_redis('bootstrap',inv_collection['Lab_Name'])
                last_event_key = event.key
        sleep(float(interval))
except KeyboardInterrupt:
    print('\nCaught keyboard interrupt, exiting ...')
collect_events.DestroyCollector()