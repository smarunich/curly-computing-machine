#!/usr/bin/env python3
import ipam

ipam = ipam.IpamDB()


print('1:%s' % ipam.create_view('banana'))
print('2:%s' % ipam.create_network('10.0.0.0/8'))
print('3:%s' % ipam.create_network('10.0.0.0/16'))
print('4:%s' % ipam.create_network('11.0.0.0/8', view_name='banana'))
print('5:%s' % ipam.create_network('12.0.0.0/16','12.0.0.10','12.0.0.11'))
print('6:%s' % ipam.create_network('13.0.0.0/8','13.0.0.10','13.0.0.100', view_name='banana'))


for view in ipam.get_views()['views']:
    print('VIEW: %s' % view)
    for network in ipam.get_networks(view_name=view['name'])['networks']:
        print('\tNETWORK: %s' % network)

print('===')
print('A:%s' % ipam.find_network_for_ip('10.0.0.1'))
print('B:%s' % ipam.find_network_for_ip('11.0.0.1', view_name='banana'))
print('C:%s' % ipam.create_host('test_one', '10.0.0.1', fqdn='test_one.localdomain'))
print('D:%s' % ipam.create_host('test_two', '10.0.0.2', fqdn='test_two.localdomain'))
print('E:%s' % ipam.search_hosts(fqdn='test_two.localdomain'))
print('F:%s' % ipam.get_hosts('10.0.0.0/16'))
print('G:%s' % ipam.delete_host('10.0.0.2'))
print('H:%s' % ipam.search_hosts(fqdn='test_one.localdomain'))
print('I:%s' % ipam.search_hosts(fqdn='test_two.localdomain'))
print('===')

print('---')
print('Y: %s' % ipam.next_available_ip('blar', '10.0.0.0/16'))
print('---')

for i in range(3):
    print('---')
    print('Z: %s' % ipam.next_available_ip('blar', '12.0.0.0/16'))
    print('---')

print('5:%s' % ipam.delete_network('11.0.0.0/8', view_name='banana'))
print('6:%s' % ipam.delete_network('10.0.0.0/8'))
print('7:%s' % ipam.delete_view('banana'))

for view in ipam.get_views()['views']:
    print('VIEW: %s' % view)
    for network in ipam.get_networks(view_name=view['name'])['networks']:
        print('\tNETWORK: %s' % network)
