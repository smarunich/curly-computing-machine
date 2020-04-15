#!/usr/bin/env python3
import requests
import boto3
import redis
import json
import psutil
import os
import signal


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


class update_redis(object):
    def __init__(self, redis_session, id):
        self.redis_session = redis_session
        self.identity = identity(id)
        self.redis_instances()

    def redis_instances(self):
        old_identity = r.hgetall(self.identity.Name)
        if old_identity:
            self.old_identity = identity(document=old_identity)
            r.srem(self.old_identity.Lab_Group, self.old_identity.ipAddress)
        r.hmset(self.identity.Name, self.identity())
        r.sadd(self.identity.Lab_Group, self.identity.ipAddress)
        r.sadd('groups', self.identity.Lab_Group)
        r.sadd('names', self.identity.Name)


if __name__ == '__main__':
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    p = r.pubsub()
    p.subscribe('instances')
    for m in p.listen():
        if m['type'] == 'message':
            data = json.loads(m['data'].decode('utf-8'))
            id = list(data.keys())[0]
            hosts_file(data[id]['ipAddress'], data[id]['Lab_Name'])
            update_redis(r, data[id])
            r.publish('bootstrap', json.dumps({'bootstrap': data[id]['Lab_Name']}))
