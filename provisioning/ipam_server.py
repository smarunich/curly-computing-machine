#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests

Build a cert/key pair with
openssl req -new -x509 -keyout ipam.pem -out ipam.crt -days 365 -nodes

Usage::
    ./server.py [<port>] - needs to be 443
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import apsw
import ssl
import json
import logging
import ipam

ipamdb = ipam.IpamDB()


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.parsed_url = urlparse(str(self.path))
        logging.info(self.parsed_url)
        self._set_response()
        if self.parsed_url.query == '_schema':
            logging.info("making up a schema")
            response = {'supported_versions': ['1.6']}
        else:
            response = self.router_get(self.parsed_url.path)
        self.wfile.write('{}'.format(json.dumps(response)).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        self.parsed_url = urlparse(str(self.path))
        logging.info(self.parsed_url)
        self.post_data = json.loads(self.rfile.read(content_length))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), self.post_data)
        self._set_response()

        response = self.router_post(self.parsed_url.path)

        self.wfile.write("{}".format(json.dumps(response)).encode('utf-8'))

    def do_DELETE(self):
        logging.info("DELETE request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.parsed_url = urlparse(str(self.path))
        parts = self.parsed_url.path.split('/')
        if parts[3] == 'record:host':
            (ip, name) = parts[4].split(':')
            print('DELETE: %s' % ipamdb.delete_host(ip))
        self._set_response()

    def router_get(self, path):
        parts = path.split('/')
        if parts[-1] == 'view' or parts[-1] == 'networkview':
            return ipamdb.get_views()['views']
        if parts[-1] == 'network':
            networks = ipamdb.get_networks()['networks']
            response = {'result': []}
            for network in networks:
                response['result'].append({'network': network['cidr']})
            return response
        if parts[-1] == 'record:host':
            (k, v) = self.parsed_url.query.split('=')
            if k == 'name':
                hosts = ipamdb.search_hosts(name=v)
                print('FOUND: %s' % hosts)
                if hosts['count'] == 1:
                    response = [
                        {'_ref': 'record:host/%s:%s/' % (hosts['hosts'][0]['ip_address'], hosts['hosts'][0]['name'])}]
                    return response

    def router_post(self, path):
        parts = path.split('/')
        if parts[-1] == 'record:host':
            addr_parts = self.post_data['ipv4addrs'][0]['ipv4addr'].split(':')
            if addr_parts[0] == 'func' and addr_parts[1] == 'nextavailableip':
                name = self.post_data['name']
                (cidr, view) = addr_parts[2].split(',')
                host = ipamdb.next_available_ip(name, cidr, view_name=view)
                self.post_data['ipv4addrs'][0]['ipv4addr'] = host['ip_address']
                return self.post_data

    def list_networks(self):
        nets = {'result': [{'network': '1.2.3.0/24'}, {'network': '2.3.4.0/24'}]}
        return nets


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   certfile='ipam.pem',
                                   ssl_version=ssl.PROTOCOL_TLSv1)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
