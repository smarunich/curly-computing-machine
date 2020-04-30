import ipam

ipam = ipam.IpamDB()
print('5:%s' % ipam.create_network('12.0.0.0/16','12.0.0.10','12.0.0.11'))