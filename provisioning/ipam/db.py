import apsw
import ipaddress


class IpamDB(object):
    views_table = '''CREATE TABLE IF NOT EXISTS views (
                        id integer PRIMARY KEY,
                        name text NOT NULL,
                        UNIQUE(id, name)
                    );'''
    networks_table = '''CREATE TABLE IF NOT EXISTS networks (
                        id integer PRIMARY KEY,
                        view_id integer NOT NULL,
                        cidr text NOT NULL,
                        allocation_start text NULL,
                        allocation_end text NULL,
                        FOREIGN KEY (view_id) REFERENCES views(id)
                    );'''
    hosts_table = '''CREATE TABLE IF NOT EXISTS hosts (
                        id integer PRIMARY KEY,
                        view_id integer NOT NULL,
                        network_id integer NOT NULL,
                        name text NOT NULL,
                        ip_address text NOT NULL,
                        fqdn text,
                        FOREIGN KEY (network_id) REFERENCES networks(id),
                        FOREIGN KEY (view_id) REFERENCES views(id)
                    );'''

    def __init__(self, db_file='ipam.sqlite'):
        self.db_file=db_file
        self._initialise()

    def _initialise(self):
        self._create_connection()
        for table in [IpamDB.views_table, IpamDB.networks_table, IpamDB.hosts_table]:
            self._create_table(table)
        self.create_view('default')

    def _create_connection(self):
        self.conn = None
        try:
            self.conn = apsw.Connection(self.db_file)
        except Exception as e:
            print(e)

    def _create_table(self, sql):
        try:
            c = self.conn.cursor()
            c.execute(sql)
        except Exception as e:
            print(e)

    def create_view(self, view_name):
        insert = "INSERT INTO views(name) VALUES(?)"
        cur = self.conn.cursor()
        view = self.get_view(view_name)
        if not view:
            cur.execute(insert, (view_name,))
            view = self.get_view(view_name)
        return view

    def delete_view(self, view_name, force=False):
        # TODO Check for existing networks in view
        # TODO implement force removal of view
        view = self.get_view(view_name)
        if view:
            delete = "DELETE FROM views WHERE id=?"
            cur = self.conn.cursor()
            cur.execute(delete, (view['id'],))

    def get_view(self, view_name):
        select = "SELECT id, name FROM views WHERE name=?"
        cur = self.conn.cursor()
        try:
            *_, row = cur.execute(select, (view_name,))
            row = {'id': row[0], 'name': row[1]}
        except ValueError as e:
            row = None
        return row

    def get_views(self):
        result = {'views': [], 'count': 0}
        select = "SELECT * FROM views;"
        cur = self.conn.cursor()
        for row in cur.execute(select):
            result['views'].append({'id': row[0], 'name': row[1]})
            result['count'] += 1
        return result

    def create_network(self, cidr, allocation_start='', allocation_end='', view_name='default'):
        if allocation_start == '':
            allocation_start = str(ipaddress.IPv4Network(cidr)[0])
            allocation_end = str(ipaddress.IPv4Network(cidr)[-1])
        try:
            view_id = self.get_view(view_name=view_name)['id']
        except TypeError as e:
            return None
        insert = "INSERT INTO networks(cidr, allocation_start, allocation_end, view_id) VALUES(?,?,?,?)"
        cur = self.conn.cursor()
        network = self.get_network(cidr, view_name)
        if not network:
            cur.execute(insert, (cidr, allocation_start, allocation_end, view_id))
            network = self.get_network(cidr, view_name)
        return network

    def delete_network(self, cidr, view_name='default', force=False):
        # TODO Check for existing records in network
        # TODO implement force removal of network
        network = self.get_network(cidr, view_name)
        if network:
            view_id = self.get_view(view_name=view_name)['id']
            delete = "DELETE FROM networks WHERE id=? AND view_id=?"
            cur = self.conn.cursor()
            cur.execute(delete, (network['id'], view_id))

    def get_network(self, cidr, view_name='default'):
        view = self.get_view(view_name=view_name)
        select = "SELECT id, cidr, allocation_start, allocation_end FROM networks WHERE cidr=? AND view_id=?"
        cur = self.conn.cursor()
        try:
            *_, row = cur.execute(select, (cidr, view['id']))
            network = {'id': row[0], 'cidr': row[1], 'allocation_start': row[2], 'allocation_end': row[3], 'view': view}
        except ValueError as e:
            network = None
        return network

    def get_networks(self, view_name='default'):
        view = self.get_view(view_name=view_name)
        result = {'networks': [], 'count': 0}
        select = "SELECT * FROM networks WHERE view_id=?"
        cur = self.conn.cursor()
        for row in cur.execute(select, (view['id'],)):
            result['networks'].append({'id': row[0], 'cidr': row[2], 'view': view})
            result['count'] += 1
        return result

    def create_host(self, name, ip, fqdn=None, view_name='default'):
        try:
            vid = self.get_view(view_name=view_name)['id']
            nid = self.find_network_for_ip(ip, view_name=view_name)['id']
        except TypeError as e:
            return None
        insert = "INSERT INTO hosts(name, ip_address, fqdn, network_id, view_id) VALUES(?,?,?,?,?)"
        cur = self.conn.cursor()
        host = self.get_host(ip, view_name=view_name)
        if not host:
            cur.execute(insert, (name, ip, fqdn, nid, vid))
            host = self.get_host(ip, view_name=view_name)
        return host

    def delete_host(self, ip, view_name='default'):
        host = self.get_host(ip, view_name=view_name)
        if host:
            view_id = self.get_view(view_name=view_name)['id']
            network_id = self.get_network(host['network']['cidr'])['id']
            delete = "DELETE FROM hosts WHERE id=? AND network_id=? AND view_id=?"
            cur = self.conn.cursor()
            cur.execute(delete, (host['id'], network_id, view_id))

    def get_host(self, ip, view_name='default'):
        try:
            vid = self.get_view(view_name=view_name)['id']
        except TypeError as e:
            return None
        network = self.find_network_for_ip(ip, view_name=view_name)
        host = None
        if network:
            select = "SELECT id, name, ip_address, fqdn FROM hosts WHERE ip_address=? AND network_id=? AND view_id=?"
            cur = self.conn.cursor()
            try:
                *_, row = cur.execute(select, (ip, network['id'], vid))
                host = {'id': row[0], 'name': row[1], 'ip_address': row[2], 'fqdn': row[3], 'network': network}
            except ValueError as e:
                pass
        return host

    def get_hosts(self, network_cidr, view_name='default'):
        try:
            vid = self.get_view(view_name=view_name)['id']
            network = self.get_network(network_cidr, view_name=view_name)
            nid = network['id']
        except TypeError as e:
            return None
        result = {'hosts': [], 'count': 0, 'network': network}
        select = "SELECT * FROM hosts WHERE network_id=? AND view_id=?"
        cur = self.conn.cursor()
        for row in cur.execute(select, (nid, vid)):
            result['hosts'].append({'id': row[0], 'name': row[3], 'ip_address': row[4], 'fqdn': row[5]})
            result['count'] += 1
        return result

    def next_available_ip(self, name, cidr, fqdn=None, view_name='default'):
        network = self.get_network(cidr)
        if network:
            hosts = self.get_hosts(network['cidr'])
            for ip_addr in ipaddress.ip_network(network['cidr']).hosts():
                if ip_addr < ipaddress.IPv4Address(network['allocation_start']):
                    continue
                if ip_addr > ipaddress.IPv4Address(network['allocation_end']):
                    return False
                if str(ip_addr) not in list(map(lambda x: x['ip_address'], hosts['hosts'])):
                    return self.create_host(name, str(ip_addr), fqdn=fqdn, view_name=view_name)


    def find_network_for_ip(self, ip, view_name='default'):
        networks = self.get_networks(view_name=view_name)
        ip_found = None
        result = None
        for network in networks['networks']:
            ip_addr = ipaddress.ip_address(ip)
            ip_net = ipaddress.ip_network(network['cidr'])
            if ip_addr in ip_net:
                if not ip_found:
                    ip_found = ip_net
                    result = network
                elif ip_net.prefixlen > ip_found.prefixlen:
                    ip_found = ip_net
                    result = network
        return result

    def search_hosts(self, name=None, ip=None, fqdn=None, view_name='default'):
        view = self.get_view(view_name=view_name)
        if name is None and ip is None and fqdn is None:
            raise Exception('Must supply host locator details')
        if name is not None:
            nsel = "name = '%s'" % name
        else:
            nsel = ''
        if ip is not None:
            isel = "ip_address = '%s'" % ip
        else:
            isel = ''
        if fqdn is not None:
            fsel = "fqdn = '%s'" % fqdn
        else:
            fsel = ''
        selector = ''
        for sel in [nsel, isel, fsel]:
            if selector == '':
                selector = sel
            else:
                if sel is not '':
                    selector = selector + ' AND ' + sel
        select = "SELECT * FROM hosts WHERE " + selector + ' AND view_id=%s' % view['id']
        cur = self.conn.cursor()
        result = {'hosts': [], 'count': 0}
        for row in cur.execute(select):
            result['hosts'].append({'id': row[0], 'network_id': row[2], 'name': row[3], 'ip_address': row[4], 'fqdn': row[5], 'view': view})
            result['count'] += 1
        return result
