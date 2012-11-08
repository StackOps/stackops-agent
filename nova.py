#   Copyright 2011 STACKOPS TECHNOLOGIES S.L.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Created on Aug 1, 2012

@author: Diego Parrilla
"""
import getpass
import os
import shutil
import install
import re

import utils

from configuration import Config

class NovaApiConfig(Config):
    _filename = "nova-api-stackops.conf"

    def __init__(self):
        """
        Constructor
        """
        self.TOKEN_SIZE = 8

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # EC2 API Configuration
        self.ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname', '127.0.0.1')
        self.ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz', '127.0.0.1')
        self.ec2_port = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz_port', '8773')

        # Openstack API Configuration
        self.osapi_port = self._filler.getPropertyValue(xmldoc, 'osapi', 'dmz_port', '8774')

        # S3 API configuration
        self.s3_hostname = self._filler.getPropertyValue(xmldoc, 's3', 'hostname', self.ec2_hostname)
        self.s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz', self.ec2_dmz)
        self.s3_port = self._filler.getPropertyValue(xmldoc, 's3', 'port', '3333')

        # GLANCE Service configuration
        self.glance_hostname = self._filler.getPropertyValue(xmldoc, 'glance', 'hostname', self.ec2_hostname)
        self.glance_port = self._filler.getPropertyValue(xmldoc, 'glance', 'port', '9292')
        self.image_service = self._filler.getPropertyValue(xmldoc, 'glance', 'image_service',
            'nova.image.glance.GlanceImageService')

        # KEYSTONE Service configuration
        self.keystone_host = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_host', self.ec2_hostname)
        self.keystone_user_port = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_user_port', '5000')
        self.keystone_admin_port = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_admin_port', '32357')

        # Keystone admin password
        self.admin_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'admin_password', 'password')

        # My IP
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = self.whatIsMyIp(self.management_interface)

        # api paste configuration
        self.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        self.allow_admin_api = self._filler.getPropertyValue(xmldoc, 'osapi', 'allow_admin_api', 'true')

        # Quotas
        self.quota_instances = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_instances', '4096')
        self.quota_cores = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_cores', '8192')
        self.quota_ram = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_ram', str(1024 * 1024 * 20))
        self.quota_volumes = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_volumes', '8192')
        self.quota_gigabytes = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_gigabytes', str(1024 * 20))
        self.quota_floating_ips = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_floating_ips', '254')
        self.quota_metadata_items = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_metadata_items', '128')
        self.quota_max_injected_files = self._filler.getPropertyValue(xmldoc, 'scheduler', 'quota_max_injected_files',
            '5')
        self.quota_max_injected_file_content_bytes = self._filler.getPropertyValue(xmldoc, 'scheduler',
            'quota_max_injected_file_content_bytes', str(10 * 1024))
        self.quota_max_injected_file_path_bytes = self._filler.getPropertyValue(xmldoc, 'scheduler',
            'quota_max_injected_file_path_bytes', '255')

        # Flavors configuration
        self.set_flavors = self._filler.getPropertyValue(xmldoc, 'flavors', 'delete_default', 'false') == 'true'
        if self.set_flavors:
            self.flavors_list = self._filler.getPropertyValue(xmldoc, 'flavors', 'list', '[]')
        else:
            self.flavors_list = '[]'

        return

    def _configureNovaApi(self):
        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      # NOVA-API SPECIFIC
                      'enabled_apis': 'ec2,osapi_compute,osapi_volume,metadata',
                      'auth_strategy': 'keystone',
                      'ec2_host': self.ec2_hostname,
                      'ec2_dmz_host': self.ec2_dmz,
                      'ec2_port': self.ec2_port,
                      's3_host': self.s3_hostname,
                      's3_dmz': self.s3_dmz,
                      's3_port': self.s3_port,
                      'osapi_compute_listen_port': self.osapi_port,
                      'keystone_ec2_url': '%s://%s:%s/v2.0/ec2tokens' % (
                          'http', self.keystone_host, self.keystone_user_port),
                      'api_paste_config': self.api_paste_config,
                      'allow_admin_api': self.allow_admin_api,
                      'use_deprecated_auth': 'false',
                      # GLANCE SPECIFIC
                      'image_service': self.image_service,
                      'glance_api_servers': '%s:%s' % (self.glance_hostname, self.glance_port),
                      'quota_instances': self.quota_instances,
                      'quota_cores': self.quota_cores,
                      'quota_ram': self.quota_ram,
                      'quota_volumes': self.quota_volumes,
                      'quota_gigabytes': self.quota_gigabytes,
                      'quota_floating_ips': self.quota_floating_ips,
                      'quota_metadata_items': self.quota_metadata_items,
                      'quota_max_injected_files': self.quota_max_injected_files,
                      'quota_max_injected_file_content_bytes': self.quota_max_injected_file_content_bytes,
                      'quota_max_injected_file_path_bytes': self.quota_max_injected_file_path_bytes}

        self._writeFile(self._filename, parameters)
        utils.execute("service nova-api stop", check_exit_code=False)
        utils.execute(
            "sed -i 's/%%SERVICE_PASSWORD%%/%s/g' /etc/nova/api-paste.ini" % self.admin_password)
        utils.execute(
            "sed -i 's/%%SERVICE_TENANT_NAME%%/%s/g' /etc/nova/api-paste.ini" % 'service')
        utils.execute(
            "sed -i 's/%%SERVICE_USER%%/%s/g' /etc/nova/api-paste.ini" % 'nova')
        utils.execute('rm -f /etc/nova/nova.conf', check_exit_code=False)
        utils.execute('ln -s /etc/nova/nova-api-stackops.conf /etc/nova/nova.conf', check_exit_code=False)
        if os.path.exists(self.state_path):
            utils.execute('chown nova:nova -R %s' % self.state_path)
        utils.execute("service nova-api start")
        utils.execute("nova-manage db sync")
        return

    def _generateToken(self):
        return os.urandom(self.TOKEN_SIZE).encode("hex")

    def _deleteFlavors(self):
        # Get flavors
        (out, err) = utils.execute('nova-manage flavor list')
        old_flavors = out.split('\n')
        flavorids = []
        for str in old_flavors:
            if len(str) > 0:
                (flavorid, err) = utils.execute("echo '%s' | sed 's/: Memory:\(.*\)//g'" % str)
                flavorids.append(flavorid)
        for flavor in flavorids:
            utils.execute('nova-manage flavor delete %s' % flavor)

    def _addFlavors(self):
        # Add flavors
        flavors = eval(self.flavors_list)
        for str in flavors:
            flavor = str.split(';')
            name = flavor[0]
            memory = flavor[1]
            cpu = flavor[2]
            root_gb = flavor[3]
            flavorid = flavor[4]
            ephemeral_gb = '0'
            if len(flavor) > 5:
                ephemeral_gb = flavor[5]
            utils.execute(
                'nova-manage flavor create --name=%s --memory=%s --cpu=%s --root_gb=%s --flavor=%s --ephemeral_gb=%s' % (
                    name, memory, cpu, root_gb, flavorid, ephemeral_gb))

    def install(self, hostname):
        """
        Install all stuff needed to run NovaApi for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureNovaApi()
                if self.set_flavors:
                    self._deleteFlavors()
                self._addFlavors()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        NovaApi uninstall process
        """
        utils.execute("apt-get -y --purge remove nova-api", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        shutil.rmtree('/var/lib/nova', ignore_errors=True)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('nova-api', interactive=False)
        return


class NovaSchedulerConfig(Config):
    _filename = "nova-scheduler-stackops.conf"

    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # My IP
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = self.whatIsMyIp(self.management_interface)

        # NOVA-SCHEDULER configruration
        self.scheduler_max_cores = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_cores', '16')
        self.scheduler_max_gigabytes = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_gigabytes', '2048') # 2TB
        self.scheduler_max_networks = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_networks', '1000')
        self.scheduler_driver = self._filler.getPropertyValue(xmldoc, 'scheduler', 'driver',
            'nova.scheduler.simple.SimpleScheduler')

        return

    def _configureNovaScheduler(self):
        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      # NOVA-SCHEDULER SPECIFIC
                      'scheduler_driver': self.scheduler_driver,
                      'max_cores': self.scheduler_max_cores,
                      'max_gigabytes': self.scheduler_max_gigabytes,
                      'max_networks': self.scheduler_max_networks}

        self._writeFile(self._filename, parameters)
        utils.execute("service nova-scheduler stop", check_exit_code=False)
        if os.path.exists(self.state_path):
            utils.execute('chown nova:nova -R %s' % self.state_path)
        utils.execute("service nova-scheduler start")
        return

    def install(self, hostname):
        """
        Install all stuff needed to run NovaScheduler for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureNovaScheduler()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        NovaScheduler uninstall process
        """
        utils.execute("apt-get -y --purge remove nova-scheduler", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('nova-scheduler', interactive=False)
        return


class NovaNetworkConfig(Config):
    _filename = "nova-network-stackops.conf"

    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # NOVA-NETWORK SPECIFIC
        self.dhcpbridge = self._filler.getPropertyValue(xmldoc, 'dhcpbridge', 'process', '/usr/bin/nova-dhcpbridge')
        self.dhcpbridge_flagfile = self._filler.getPropertyValue(xmldoc, 'dhcpbridge', 'file',
            '/etc/nova/nova-network-stackops.conf')
        if self.dhcpbridge_flagfile == '/etc/nova/nova-network.conf':
            self.dhcpbridge_flagfile = '/etc/nova/nova-network-stackops.conf'
        self.routing_source_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'routing_source_ip', None)
        self.floating_range = self._filler.getPropertyValue(xmldoc, 'interfaces', 'floating_range', None)

        # Default Fixed range configuration
        self.network_manager = self._filler.getPropertyValue(xmldoc, 'network', 'type',
            'nova.network.manager.FlatDHCPManager')
        self.fixed_range = self._filler.getPropertyValue(xmldoc, 'network', 'fixed_range', '10.0.0.0/8')
        self.network_size = self._filler.getPropertyValue(xmldoc, 'network', 'network_size', '256')
        self.network_number = self._filler.getPropertyValue(xmldoc, 'network', 'network_number', '1')
        self.vlanstart = self._filler.getPropertyValue(xmldoc, 'network', 'vlanstart', '100')
        self.bridge = self._filler.getPropertyValue(xmldoc, 'network', 'bridge', 'br100')
        self.dns1 = self._filler.getPropertyValue(xmldoc, 'network', 'dns1', '8.8.8.8')
        self.dns2 = self._filler.getPropertyValue(xmldoc, 'network', 'dns2', '8.8.4.4')

        # Interfaces configuration
        self.flat_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'flat_interface')
        self.public_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_interface')
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.bridged_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'bridged_interface',
            self.flat_interface)
        iface_list = self._operatingsystem.getNetworkConfiguration()
        for iface in iface_list:
            if iface['name'] == self.management_interface:
                self.my_ip = iface['address']
            if self.routing_source_ip is None:
                if iface['name'] == self.public_interface:
                    self.routing_source_ip = iface['address']

        self.public_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip', '')
        self.public_ip_mask = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip_mask', '255.255.255.255')
        self.public_ip_gateway = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip_gateway', '')
        self.firewall_public_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'firewall_public_ip',
            'false') == 'true'

        octets = self.fixed_range.split('/')[0].split('.')
        self.flat_network_dhcp_start = '%s.%s.%s.%i' % (octets[0], octets[1], octets[2], int(octets[3]) + 2)

        return

    def _configureNovaNetwork(self):
        if os.path.exists('/usr/bin/nova-dhcpbridge'):
            self.dhcpbridge = '/usr/bin/nova-dhcpbridge'
        if os.path.exists('/var/lib/nova/bin/nova-dhcpbridge'):
            self.dhcpbridge = '/var/lib/nova/bin/nova-dhcpbridge'
        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      # NOVA-NETWORK SPECIFIC
                      'dhcpbridge': self.dhcpbridge,
                      'dhcpbridge_flagfile': self.dhcpbridge_flagfile,
                      'routing_source_ip': self.routing_source_ip,
                      'public_interface': self.public_interface,
                      'network_manager': self.network_manager,
                      'flat_network_dhcp_start': self.flat_network_dhcp_start,
                      'force_dhcp_release': 'true',
                      'fixed_range': self.fixed_range,
                      'vlan_interface': self.flat_interface,
                      'flat_interface': self.flat_interface}

        self._writeFile(self._filename, parameters)
        utils.execute("service nova-network stop", check_exit_code=False)
        if os.path.exists(self.state_path):
            utils.execute('chown nova:nova -R %s' % self.state_path)
        utils.execute("service nova-network start")
        return

    def _addFloatingIP(self, ip_list):
        # Add floating ips
        if ip_list.startswith('['):
            ips = eval(ip_list)
            for ip in ips:
                utils.execute('nova-manage --flagfile=%s float create %s' % ('/etc/nova/nova-network-stackops.conf', ip))
        else:
            utils.execute(
                'nova-manage --flagfile=%s float create %s' % ('/etc/nova/nova-network-stackops.conf', ip_list))

    def _addFirewallRules(self, publicip, bridgeif):
        utils.execute("service iptables-persistent flush", check_exit_code=False)
        shutil.copyfile('/var/lib/stackops/rules.iptables', '/etc/iptables/rules.v4')
        utils.execute("sed -i 's/127.0.0.1/%s/g' /etc/iptables/rules.v4" % publicip)
        utils.execute("sed -i 's/BRIDGEIF/%s/g' /etc/iptables/rules.v4" % bridgeif)
        utils.execute("service iptables-persistent start")

    def _addDummyIF(self, hostname):
        if hostname == 'nova-controller':
            utils.execute('echo "dummy" >> /etc/modules')
            utils.execute('modprobe dummy')
            utils.execute('ifconfig dummy0 0.0.0.0')

    def _configurePublicIP(self):
        # Remove old configurations, if any
        utils.execute("sed -i '{:q;N;s/\\tpost-up[^][^]*.\\n//g;t q}' /etc/network/interfaces")
        # Configure Public interface
        for networkType in ['static', 'dhcp']:
            # enable flat interface
            utils.execute(
                "sed -i 's/inet %s/inet %s\\n\\tpost-up ifconfig %s 0.0.0.0/g' /etc/network/interfaces" % (
                    networkType, networkType, self.flat_interface))
            # Configure Public interface
            if self.public_ip_mask != '255.255.255.255':
                utils.execute(
                    "sed -i 's/inet %s/inet %s\\n\\tpost-up ifconfig %s %s netmask %s\\n\\tpost-up route add default gw %s %s/g' /etc/network/interfaces" % (
                        networkType, networkType, self.public_interface, self.public_ip, self.public_ip_mask,
                        self.public_ip_gateway, self.public_interface))
        utils.execute('ifconfig ' + self.flat_interface + ' 0.0.0.0')
        if self.public_ip_mask != '255.255.255.255':
            utils.execute(
                'ifconfig %s %s netmask %s' % (self.public_interface, self.public_ip, self.public_ip_mask))
            utils.execute('route del default', check_exit_code=False)
            utils.execute('route add default gw %s %s' % (self.public_ip_gateway, self.public_interface))


    def _createDefaultNetworks(self):
        if self.network_manager == 'nova.network.manager.VlanManager':
            utils.execute(
                'nova-manage --flagfile=%s network create service %s %s %s --vlan=%s --bridge_interface=%s --dns1=%s --dns2=%s' % (
                    '/etc/nova/nova-network-stackops.conf', self.fixed_range, self.network_number, self.network_size,
                    self.vlanstart, self.bridged_interface,
                    self.dns1,
                    self.dns2))
            bridgeif = 'br%s' % self.vlanstart
        else:
            utils.execute(
                'nova-manage  --flagfile=%s network create service %s %s %s --bridge=%s --bridge_interface=%s --dns1=%s --dns2=%s' % (
                    '/etc/nova/nova-network-stackops.conf', self.fixed_range, self.network_number, self.network_size,
                    self.bridge, self.bridged_interface,
                    self.dns1, self.dns2))
            bridgeif = 'br100'
        return bridgeif

    def _enableForwarding(self):
        # enable ipforwarding
        utils.execute("sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf")
        utils.execute("sysctl -p /etc/sysctl.conf")


    def install(self, hostname):
        result = ''
        try:
            # Install packages for component
            self.installPackages()
            self._addDummyIF(hostname)
            self._configurePublicIP()
            self._enableForwarding()
            self._configureNovaNetwork()
            bridgeif = self._createDefaultNetworks()
            self._addFloatingIP(self.floating_range)
            # add firewall to public ip if necessary
            if self.firewall_public_ip and len(self.public_ip) > 0:
                self._addFirewallRules(self.public_ip, bridgeif)
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        NovaNetwork uninstall process
        """
        # Remove old configurations, if any
        utils.execute("sed -i '{:q;N;s/\\tpost-up[^][^]*.\\n//g;t q}' /etc/network/interfaces")
        # Remove packages

        shutil.rmtree('/var/lock/nova/nova-iptables.lock', ignore_errors=True)

        utils.execute("apt-get -y --purge remove nova-network iptables-persistent", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        shutil.rmtree('/var/lock/nova/nova-iptables.lock', ignore_errors=True)
        self.installPackagesCommon()
        self._installDeb('nova-network', interactive=False)
        if self.firewall_public_ip and len(self.public_ip) > 0:
            self._installDeb('iptables-persistent', interactive=False)
        return


class NovaComputeConfig(Config):
    _filename = "nova-compute-stackops.conf"

    PAGE_SIZE = 2 * 1024 * 1024
    BONUS_PAGES = 40

    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # My IP
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = self.whatIsMyIp(self.management_interface)

        # GLANCE Service configuration
        self.glance_hostname = self._filler.getPropertyValue(xmldoc, 'glance', 'hostname', 'localhost')
        self.glance_port = self._filler.getPropertyValue(xmldoc, 'glance', 'port', '9292')
        self.image_service = self._filler.getPropertyValue(xmldoc, 'glance', 'image_service',
            'nova.image.glance.GlanceImageService')

        # NOVA-VNCPROXY configruration
        self.public_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip', '')
        if len(self.public_ip) > 0:
            self.vncproxy_host = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'host', self.public_ip)
        else:
            self.ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname', '127.0.0.1')
            self.vncproxy_host = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'host', self.ec2_hostname)
        self.vncproxy_port = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'port', '6080')
        self.vncproxy_type = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'type', 'http')

        # NOVA-COMPUTE KVM specific
        self.libvirt_type = self._filler.getPropertyValue(xmldoc, 'libvirt', 'type')

        # ISCSI connectivity
        self.iscsi_ip_prefix = self._filler.getPropertyValue(xmldoc, 'iscsi', 'ip_prefix')
        self.num_targets = self._filler.getPropertyValue(xmldoc, 'iscsi', 'num_targets')
        self.storage_hostname = self._filler.getPropertyValue(xmldoc, 'iscsi', 'storage_hostname', 'nova-volume')

        # Network interfaces
        self.flat_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'flat_interface', 'eth1')

        # Connect to shared filesystem
        self.instances_path = self._filler.getPropertyValue(xmldoc, 'instances_filesystem', 'instances_path',
            '%s/instances' % self.state_path)
        self.instances_filesystem_mount_type = self._filler.getPropertyValue(xmldoc, 'instances_filesystem',
            'mount_type', 'local')

        if self.instances_filesystem_mount_type == 'local':
            self.mount_point = self._filler.getPropertyValue(xmldoc, 'instances_filesystem', 'mount_point', None)
            self.mount_parameters = self._filler.getPropertyValue(xmldoc, 'instances_filesystem', 'mount_parameters',
                None)
        else:
            self.mount_point = self._filler.getPropertyValue(xmldoc, 'instances_filesystem', 'mount_point',
                '192.168.10.198:/volumes/vol1/openstack-nfs-livemigration')
            self.mount_parameters = self._filler.getPropertyValue(xmldoc, 'instances_filesystem', 'mount_parameters',
                'defaults')

        # NOVA-VOLUME QEMU Specific
        self.use_volume_nfs = self._filler.getPropertyValue(xmldoc, 'nas', 'use_nas', 'false') == 'true'
        if self.use_volume_nfs:
            self.volume_driver = self._filler.getPropertyValue(xmldoc, 'nas', 'volume_driver',
                'nova.volume.nas.QEMUDriver')
            self.volumes_path = self._filler.getPropertyValue(xmldoc, 'nas', 'volumes_path', '/var/lib/nova/volumes')
            self.volumes_mount_point = self._filler.getPropertyValue(xmldoc, 'nas', 'mount_point',
                '192.168.10.198:/volumes/vol1/openstack-nfs-volumes')
            self.volumes_mount_parameters = self._filler.getPropertyValue(xmldoc, 'nas', 'mount_parameters',
                'defaults')
        else:
            self.volume_driver = 'nova.volume.driver.ISCSIDriver'

        self.use_iscsi = self.volume_driver == 'nova.volume.driver.ISCSIDriver'
        # Boot behaviour and virtio
        self.resume_guests_state_on_host_boot = self._filler.getPropertyValue(xmldoc, 'libvirt',
            'resume_guests_state_on_host_boot',
            'true')
        self.start_guests_on_host_boot = self._filler.getPropertyValue(xmldoc, 'libvirt', 'start_guests_on_host_boot',
            'false')
        self.libvirt_use_virtio_for_bridges = self._filler.getPropertyValue(xmldoc, 'libvirt',
            'libvirt_use_virtio_for_bridges', 'true')

        self.hugepages = self._filler.getPropertyValue(xmldoc, 'libvirt', 'hugepages', 'false') == 'true'
        self.hugepages_percentage = self._filler.getPropertyValue(xmldoc, 'libvirt', 'hugepages_percentage', '100')

        self.minimum_root_size = self._filler.getPropertyValue(xmldoc, 'libvirt', 'minimum_root_size', '1')

        return

    def _configureNovaCompute(self):
        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      # NOVA-VNCPROXY SPECIFIC
                      'novncproxy_base_url': '%s://%s:%s/vnc_auto.html' % (
                          self.vncproxy_type, self.vncproxy_host, self.vncproxy_port),
                      'novnc_enable': 'true',
                      'vncserver_proxyclient_address': self.my_ip,
                      'vncserver_listen': '0.0.0.0',
                      # NOVA-COMPUTE SPECIFIC
                      'auth_strategy': 'keystone',
                      'connection_type': 'libvirt',
                      'minimum_root_size': self.minimum_root_size,
                      'volume_driver': self.volume_driver,
                      'image_service': self.image_service,
                      'glance_api_servers': '%s:%s' % (self.glance_hostname, self.glance_port),
                      'libvirt_type': self.libvirt_type,
                      'iscsi_ip_prefix': self.iscsi_ip_prefix,
                      'num_targets': self.num_targets,
                      'instances_path': self.instances_path,
                      'resume_guests_state_on_host_boot': self.resume_guests_state_on_host_boot,
                      'start_guests_on_host_boot': self.start_guests_on_host_boot,
                      'libvirt_use_virtio_for_bridges': self.libvirt_use_virtio_for_bridges}

        try:
            self._writeFile(self._filename, parameters)
        except Exception as e:
            print e
        utils.execute("service nova-compute stop", check_exit_code=False)
        utils.execute("rm -f /etc/nova/nova-compute.conf", check_exit_code=True)
        if os.path.exists(self.state_path):
            utils.execute('chown nova:nova -R %s' % self.state_path)
        utils.execute("service nova-compute start")
        return

    def _configureFlatInterface(self, hostname):
        if hostname != 'nova-controller':
            # Remove old configurations, if any
            utils.execute("sed -i '{:q;N;s/\\tpost-up[^][^]*.\\n//g;t q}' /etc/network/interfaces")
            for networkType in ['static', 'dhcp']:
                # enable flat interface
                utils.execute(
                    "sed -i 's/inet %s/inet %s\\n\\tpost-up ifconfig %s 0.0.0.0/g' /etc/network/interfaces" % (
                        networkType, networkType, self.flat_interface))
            utils.execute('ifconfig ' + self.flat_interface + ' 0.0.0.0')

    def _configureNFS(self):
        # configure NFS mount
        if os.path.ismount(self.instances_path):
            utils.execute('umount %s' % self.instances_path)
        mpoint = '%s %s nfs %s 0 0' % (self.mount_point, self.instances_path, self.mount_parameters)
        utils.filter_file(lambda l:mpoint not in l, '/etc/fstab')
        utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
        # mount NFS remote
        try:
            utils.execute('mount -a')
        except Exception as e:
            utils.filter_file(lambda l:mpoint not in l, '/etc/fstab')
            raise e

    def _configureVolumeNFS(self):
        # configure NFS volumes mount
        if not os.path.exists(self.volumes_path):
            utils.execute('mkdir -p %s' % self.volumes_path, check_exit_code=False)
        if os.path.ismount(self.volumes_path):
            utils.execute('umount %s' % self.volumes_path)
        mpoint = '%s %s nfs %s 0 0' % (self.volumes_mount_point, self.volumes_path, self.volumes_mount_parameters)
        utils.filter_file(lambda l:mpoint not in l, '/etc/fstab')
        utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
        # mount NFS remote
        try:
            utils.execute('mount -a')
        except Exception as e:
            utils.filter_file(lambda l:mpoint not in l, '/etc/fstab')
            raise e

    def _configureNovaVolumeHost(self):
        # add to /etc/hosts file the hostname of nova-volume
        utils.execute('echo "\n' + self.iscsi_ip_prefix + '\t' + self.storage_hostname + '" >> /etc/hosts')

    def _configureHugePages(self):
        # enable huge pages in the system
        machine = install.Machine()
        pages = int(0.01 * int(self.hugepages_percentage) * int(
            machine.getMemoryAvailable() / self.PAGE_SIZE)) + self.BONUS_PAGES

        utils.execute("mkdir /dev/hugepages", check_exit_code=False)
        utils.execute('sed -i /hugetlbfs/d /etc/fstab')
        utils.execute('echo "hugetlbfs       /dev/hugepages  hugetlbfs       defaults        0 0\n" >> /etc/fstab')
        utils.execute('mount -t hugetlbfs hugetlbfs /dev/hugepages')

        utils.execute('echo "vm.nr_hugepages = %s" > /etc/sysctl.d/60-hugepages.conf' % pages)
        utils.execute('sysctl vm.nr_hugepages=%s' % pages)
        utils.execute("sysctl -p /etc/sysctl.conf")

        # modify libvirt template to enable hugepages
        utils.execute("sed -i '/hugepages/d' /usr/share/pyshared/nova/virt/libvirt.xml.template")
        utils.execute(
            "sed -i 's#</domain>#\\t<memoryBacking><hugepages/></memoryBacking>\\n</domain>#g' /usr/share/pyshared/nova/virt/libvirt.xml.template")

    def _disableSwap(self):
        utils.execute('sed -i /swap/d /etc/fstab')
        utils.execute('swapoff -a', check_exit_code=False)

    def _configureApparmor(self):
        utils.execute("sed -i '/hugepages/d' /etc/apparmor.d/abstractions/libvirt-qemu")
        utils.execute("echo '  owner /dev/hugepages/libvirt/qemu/* rw,' >> /etc/apparmor.d/abstractions/libvirt-qemu")

    def _configureLibvirt(self, hostname):
        utils.execute("service libvirt-bin stop", check_exit_code=False)
        # share libvirt configuration to restore compute nodes
        if self.instances_filesystem_mount_type == 'nfs':
            path = '%s/libvirt/%s' % (self.instances_path, hostname)
            if not os.path.exists(path):
                utils.execute('mkdir -p %s' % path, check_exit_code=False)
                utils.execute('cp -fR /etc/libvirt/* %s/' % path, check_exit_code=False)
            utils.execute('rm -fR /etc/libvirt', check_exit_code=False)
            utils.execute('ln -s %s /etc/libvirt' % path, check_exit_code=False)
            # enable communication to libvirt
        utils.execute("sed -i 's/#listen_tls = 0/listen_tls = 0/g' /etc/libvirt/libvirtd.conf")
        utils.execute("sed -i 's/#listen_tcp = 1/listen_tcp = 1/g' /etc/libvirt/libvirtd.conf")
        utils.execute('''sed -i 's/#auth_tcp = "sasl"/auth_tcp = "none"/g' /etc/libvirt/libvirtd.conf''')
        utils.execute('''sed -i 's/libvirtd_opts="-d"/libvirtd_opts="-d -l"/g' /etc/default/libvirt-bin''')
        utils.execute("service libvirt-bin start")

    def _configureGlusterFS(self):
        # configure NFS mount
        utils.execute(
            'echo "\n %s %s glusterfs %s 0 0" >> /etc/fstab' % (
                self.mount_point, self.instances_path, self.mount_parameters))
        # mount NFS remote
        utils.execute('mount -a')

    def _configureISCSI(self):
        pass

    def install(self, hostname):
        """
        Install all stuff needed to run NovaCompute for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                if hostname != 'nova-controller':
                    self._disableSwap()
                if self.hugepages and hostname != 'nova-controller':
                    self._configureHugePages()
                self.installPackages() # Install packages for component

                self._configureFlatInterface(hostname) # Configure Flat Interface
                if self.hugepages and hostname != 'nova-controller':
                    self._configureApparmor()
                if self.use_volume_nfs:
                    self._configureVolumeNFS() # Configure Volume NFS
                if self.instances_filesystem_mount_type == 'nfs':
                    self._configureNFS() # Configure NFS
                if self.instances_filesystem_mount_type == 'glusterfs':
                    self._configureGlusterFS() # Configure GlusterFS
                if self.use_iscsi:
                    if self.storage_hostname != 'nova-controller':
                        self._configureNovaVolumeHost() # Configure NovaVolume host name
                    self._configureISCSI()
                self._configureLibvirt(hostname) # Enable Libvirt communication
                self._configureNovaCompute()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        NovaCompute uninstall process
        """
        utils.execute("apt-get -y --purge remove libvirt-bin nova-compute", check_exit_code=False)
        if self.use_iscsi:
            utils.execute("apt-get -y --purge remove open-iscsi open-iscsi-utils", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        shutil.rmtree('/var/lib/libvirt', ignore_errors=True)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('libvirt-bin nova-compute', interactive=False)
        if self.use_iscsi:
            self._installDeb('open-iscsi open-iscsi-utils', interactive=False)
        if self.instances_filesystem_mount_type == 'nfs':
            self._installDeb('nfs-common')
        return


class HorizonConfig(Config):
    def __init__(self):
        """
        Constructor
        """

    # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # No configuration. Horizon time is running out...
        return

    def _configureApache(self):
        utils.execute('a2enmod proxy_http')
        utils.execute('a2enmod ssl')
        utils.execute('a2enmod rewrite')
        utils.execute('a2ensite default-ssl')
        shutil.copyfile('/var/lib/stackops/sslcert.crt', '/etc/ssl/certs/sslcert.crt')
        shutil.copyfile('/var/lib/stackops/sslcert.key', '/etc/ssl/private/sslcert.key')
        shutil.copyfile('/var/lib/stackops/apache_default.conf', '/etc/apache2/sites-available/default')
        shutil.copyfile('/var/lib/stackops/apachessl_default.conf', '/etc/apache2/sites-available/default-ssl')
        utils.execute('echo "" > /etc/apache2/conf.d/openstack-dashboard.conf')

    def _configureHorizon(self):
        utils.execute("service apache2 stop", check_exit_code=False)
        utils.execute("service apache2 start")
        return

    def install(self, hostname):
        """
        Install all stuff needed to run Horizon for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureApache()
                self._configureHorizon()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        Horizon uninstall process
        """
        utils.execute('echo "" > /etc/apache2/conf.d/openstack-dashboard.conf')
        utils.execute('echo "" > /etc/apache2/sites-available/default')
        utils.execute('echo "" > /etc/apache2/sites-available/default-ssl')
        utils.execute("apt-get -y --purge remove libapache2-mod-wsgi openstack-dashboard", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        utils.execute('rm /etc/apache2/conf.d/openstack-dashboard.conf', check_exit_code=False)
        utils.execute('echo "" > /etc/apache2/sites-available/default', check_exit_code=False)
        utils.execute('echo "" > /etc/apache2/sites-available/default-ssl', check_exit_code=False)
        self.installPackagesCommon()
        self._installDeb('libapache2-mod-wsgi', interactive=False)
        self._installDeb('openstack-dashboard --no-install-recommends', interactive=False)
        self._installDeb('openstack-dashboard-stackops-theme', interactive=False)
        css_path = "/usr/share/openstack-dashboard/openstack_dashboard/static/dashboard/css"
        utils.execute(
            "cp -f %s/stackops.css %s/style.css" % (css_path, css_path)
            , check_exit_code=False)
        img_path = "/usr/share/openstack-dashboard/openstack_dashboard/static/dashboard/img"
        utils.execute(
            "cp -f %s/favicon-stackops.ico %s/favicon.ico" % (img_path, img_path)
            , check_exit_code=False)
        utils.execute("sed -i 's/ENABLE_JUJU_PANEL = True/ENABLE_JUJU_PANEL = False/g' /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py")
        utils.execute('sed -i "/LOGIN_URL/d" /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('echo "LOGIN_URL = \'/horizon/auth/login\'" >> /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('sed -i "/LOGIN_REDIRECT_URL/d" /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('echo "LOGIN_REDIRECT_URL = \'/horizon\'" >> /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('sed -i "/MEDIA_URL/d" /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('echo "MEDIA_URL = \'/horizon/media/\'" >> /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('sed -i "/STATIC_URL/d" /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('echo "STATIC_URL = \'/horizon/static/\'" >> /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('sed -i "/ADMIN_MEDIA_PREFIX/d" /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        utils.execute('echo "ADMIN_MEDIA_PREFIX = \'/horizon/static/admin/\'" >> /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py')
        return


class NovaVncProxyConfig(Config):
    _filename = "nova-vncproxy-stackops.conf"

    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # My IP
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = self.whatIsMyIp(self.management_interface)

        # NOVA-VNCPROXY configruration
        self.vncproxy_host = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'host', self.my_ip)
        self.vncproxy_port = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'port', '6080')
        self.vncproxy_type = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'type', 'http')

        return

    def _configureNovaVncProxy(self):
        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      # NOVA-VNCPROXY SPECIFIC
                      'novncproxy_base_url': '%s://%s:%s/vnc_auto.html' % (
                          self.vncproxy_type, self.vncproxy_host, self.vncproxy_port)}

        self._writeFile(self._filename, parameters)
        utils.execute("service novnc stop", check_exit_code=False)
        utils.execute("service nova-consoleauth stop", check_exit_code=False)
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init.d/novnc" % '--flagfile=/etc/nova/nova-vncproxy-stackops.conf')
        utils.execute("service novnc start")
        utils.execute("service nova-consoleauth start")
        return

    def install(self, hostname):
        """
        Install all stuff needed to run NovaScheduler for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureNovaVncProxy()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        NovaVncProxy uninstall process
        """
        utils.execute("apt-get -y --purge remove nova-consoleauth novnc", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('nova-consoleauth novnc', interactive=False)
        return


class NovaVolumeLinuxLVMConfig(Config):
    _filename = "nova-volume-stackops.conf"

    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # My IP
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = self.whatIsMyIp(self.management_interface)

        # NOVA-VOLUME specific
        self.use_local_volumes = self._filler.getPropertyValue(xmldoc, 'iscsi', 'use_local_volumes', 'true')

        # LVM device to use as block storage
        self.lvm_device = self._filler.getPropertyValue(xmldoc, 'iscsi', 'lvm_device', None)

        return

    def _configureNovaVolumeLinuxLVM(self):
        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      # NOVA-VOLUME specific
                      'iscsi_helper': 'tgtadm',
                      'use_local_volumes': self.use_local_volumes}

        self._writeFile(self._filename, parameters)
        utils.execute("service nova-volume stop", check_exit_code=False)
        # create nova-volumes
        utils.execute('vgremove -ff nova-volumes; pvcreate -ffy ' + self.lvm_device)
        utils.execute('vgcreate nova-volumes ' + self.lvm_device)
        utils.execute("service tgt stop; service tgt start", check_exit_code=False)
        utils.execute("service nova-volume start")
        return

    def install(self, hostname):
        """
        Install all stuff needed to run NovaVolume with LinuxLVM for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureNovaVolumeLinuxLVM()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        Uninstall process
        """
        utils.execute("apt-get -y --purge remove nova-volume lvm2 tgt", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('nova-volume lvm2 tgt', interactive=False)
        return


class NexentaVolumeConfig(Config):
    '''
    classdocs
    '''

    _filename = "nova-volume.conf"

    def __init__(self):
        '''
        Constructor
        '''

    # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/tmp')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema)

        # RabbitMQ
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')

        # Network interfaces
        self.iface_list = self._operatingsystem.getNetworkConfiguration()
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        for iface in self.iface_list:
            if iface['name'] == self.management_interface:
                self.my_ip = iface['address']

        # NOVA-VOLUME Nexenta Specific
        self.use_local_volumes = self._filler.getPropertyValue(xmldoc, 'san', 'use_local_volumes', 'false')
        self.volume_driver = self._filler.getPropertyValue(xmldoc, 'san', 'volume_driver',
            'nova.volume.san.NexentaISCSIDriver')
        self.volume_group = self._filler.getPropertyValue(xmldoc, 'san', 'volume_group', 'vol1')
        self.san_thin_provision = self._filler.getPropertyValue(xmldoc, 'san', 'thin_provision', 'true')
        self.san_host = self._filler.getPropertyValue(xmldoc, 'san', 'host', '192.168.10.198')
        self.san_login = self._filler.getPropertyValue(xmldoc, 'san', 'login', 'stackops')
        self.san_password = self._filler.getPropertyValue(xmldoc, 'san', 'password', 'stackops')
        self.nova_volume_host = self._filler.getPropertyValue(xmldoc, 'san', 'nova_volume_host', 'nexenta-san')

        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'rabbit_host': self.rabbit_host,
                      'use_project_ca': self.use_project_ca,
                      'iscsi_helper': 'tgtadm',
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      'use_local_volumes': self.use_local_volumes,
                      'volume_driver': self.volume_driver,
                      'volume_group': self.volume_group,
                      'san_thin_provision': self.san_thin_provision,
                      'san_ip': self.san_host,
                      'san_login': self.san_login,
                      'san_password': self.san_password,
                      'host': self.nova_volume_host}

        self._writeFile(self._filename, parameters)
        return

    def _enableInitFiles(self):
        utils.execute('mv /etc/init/nova-volume.conf.disabled /etc/init/nova-volume.conf', None, None, False)

    def _restartServices(self):
        utils.execute('stop nova-volume; start nova-volume')

    def install(self, hostname):
        result = ''
        try:
            # Install packages for component
            self.installPackages()
            # enable controller components
            self._enableInitFiles()
            # start compute components
            self._restartServices()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('python-paramiko')


class QEMUVolumeConfig(Config):
    '''
    Use virtual images as block devices
    '''

    _filename = "nova-volume-stackops.conf"

    def __init__(self):
        '''
        Constructor
        '''

    # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # Basic common parameters
        self.verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose', 'true')
        self.nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon', 'true')
        self.auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver',
            'nova.auth.dbdriver.DbDriver')
        self.use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca', 'true')
        self.logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir', '/var/log/nova')
        self.state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path', '/var/lib/nova')
        self.lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/var/lock/nova')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'root')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_host = self._filler.getPropertyValue(xmldoc, 'database', 'host', '127.0.0.1')
        self.nova_port = self._filler.getPropertyValue(xmldoc, 'database', 'port', '3306')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'
        self.nova_charset = self._filler.getPropertyValue(xmldoc, 'database', 'charset', 'utf8')
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema, self.nova_charset)

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # My IP
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = self.whatIsMyIp(self.management_interface)


        # NOVA-VOLUME QEMU Specific
        self.volume_driver = self._filler.getPropertyValue(xmldoc, 'nas', 'volume_driver',
            'nova.volume.nas.QEMUDriver')
        self.volumes_path = self._filler.getPropertyValue(xmldoc, 'nas', 'volumes_path', '/var/lib/nova/volumes')
        self.nova_volume_host = self._filler.getPropertyValue(xmldoc, 'nas', 'host', 'nfs-server')

        # Connect to shared filesystem
        self.mount_point = self._filler.getPropertyValue(xmldoc, 'nas', 'mount_point',
            '192.168.10.198:/volumes/vol1/openstack-nfs-volumes')
        self.mount_parameters = self._filler.getPropertyValue(xmldoc, 'nas', 'mount_parameters',
            'rw,dev,noexec,nosuid,auto,nouser,noatime,async,rsize=8192,wsize=8192')

        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'root_helper': 'sudo nova-rootwrap',
                      'rabbit_host': self.rabbit_host,
                      'use_project_ca': self.use_project_ca,
                      'my_ip': self.my_ip,
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
                      'volume_driver': self.volume_driver,
                      'volumes_path': self.volumes_path,
                      'host': self.nova_volume_host}

        self._writeFile(self._filename, parameters)
        return

    def _configure(self):
        # configure NFS mount
        if not os.path.exists(self.volumes_path):
            utils.execute('mkdir -p %s' % self.volumes_path, check_exit_code=False)
        if os.path.ismount(self.volumes_path):
            utils.execute('umount %s' % self.volumes_path)
        mpoint = '%s %s nfs %s 0 0' % (self.mount_point, self.volumes_path, self.mount_parameters)
        utils.filter_file(lambda l:mpoint not in l, '/etc/fstab')
        utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
        # mount NFS remote
        utils.execute('mount -a')
        utils.execute("service nova-volume stop", check_exit_code=False)
        utils.execute("service nova-volume start")

    def install(self, hostname):
        """
        Install all stuff needed to run NovaVolume with QEMU driver for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configure()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        Uninstall process
        """
        utils.execute("apt-get -y --purge remove nova-volume nfs-common qemu-kvm", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('nova-volume nfs-common qemu-kvm', interactive=False)
        return
