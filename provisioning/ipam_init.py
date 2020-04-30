#!/usr/bin/env python3

import ipam
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--cidr', required=True)
parser.add_argument('--allocation_range', required=True)
args = parser.parse_args()

if args.cidr and args.allocation_range:
    ipam = ipam.IpamDB()
    ipam.create_network(args.cidr,args.allocation_range.split('-')[0],args.allocation_range.split('-')[1])
