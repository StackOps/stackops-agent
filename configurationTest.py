#!/usr/bin/env python
#   Copyright 2011 STACKOPS TECHNOLOGIES S.L.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
import sys
import configuration
import StackOps
import urllib
import urllib2
import utils

from twisted.python import log

from install import Filler



class MySQLConfigTest(unittest.TestCase):
    def _uninstallMySQLServer(self):
	utils.execute("apt-get -y remove --purge mysql-server python-mysqldb", check_exit_code=False)
	utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
	log.startLogging(sys.stdout)
	self._uninstallMySQLServer()
        pass
    def tearDown(self):
	self._uninstallMySQLServer()
        pass
    def testInstall(self):
        c =configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()
    	self.assertTrue(result is None)

    def testConfigure(self):
#        url = 'http://127.0.0.1:8888'
#        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
#        values = {'sysinfo' : 'Michael Foord' }
#        headers = { 'User-Agent' : user_agent }
#        data = urllib.urlencode(values)
#        req = urllib2.Request(url, data, headers)
#        response = urllib2.urlopen(req)
#        the_page = response.read()
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        c._configureMySQL()

        (stdout, stderr) = utils.execute("""mysql -uroot -p%s -e 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = "%s";'""" % (c.mysql_root_password, c.nova_schema))
        self.assertTrue(c.nova_schema in stdout)
        (stdout, stderr) = utils.execute("""mysql -uroot -p%s -e 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = "%s";'""" % (c.mysql_root_password, c.glance_schema))
        self.assertTrue(c.glance_schema in stdout)
        (stdout, stderr) = utils.execute("""mysql -uroot -p%s -e 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = "%s";'""" % (c.mysql_root_password, c.keystone_schema))
        self.assertTrue(c.keystone_schema in stdout)

class RabbitMQConfigTest(unittest.TestCase):

    def setUp(self):
        log.startLogging(sys.stdout)
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        pass
    def tearDown(self):
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        pass
    def testInstall(self):
        c =configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        self.assertTrue(result is None)
    def testConfigure(self):
        c =configuration.RabbitMQMasterConfig()
        c.installPackages()
        c._configureRabbitMQ()
        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        self.assertTrue('running' in stdout)

class KeystoneConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.KeystoneConfig()
        c.keystone_username = 'keystone'
        c.keystone_password = 'stackops'
        c.keystone_host = '127.0.0.1'
        c.keystone_port = '3306'
        c.keystone_schema = 'keystone'
        c.keystone_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (c.keystone_username, c.keystone_password, c.keystone_host, c.keystone_port,c.keystone_schema)
        c.admin_password = 'password'
        c.default_password = 'password'
        c.default_username = ''
        c.default_tenant = ''
        c.endpoint = 'http://localhost:35357/v2.0'
        c._configureKeystone()
#        (stdout, stderr) = utils.execute("service rabbitmq-server status")
#        self.assertTrue('running' in stdout)
        pass

class GlanceConfigTest(unittest.TestCase):

    MOUNT_TYPE = 'local'

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = self.MOUNT_TYPE
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.GlanceConfig()
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (c.glance_username, c.glance_password, c.glance_host, c.glance_port, c.glance_schema)
        c.glance_mount_type = self.MOUNT_TYPE
        c.admin_password = 'password'
        c._configureGlance()
        #        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        #        self.assertTrue('running' in stdout)
        pass

class NovaApiConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c = configuration.NovaApiConfig()
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        c.set_flavors = True
        c.flavors_list = "['tiny;512;1;0;999','small;1024;1;10;1000','medium;2048;2;20;1001','large;4096;4;40;1002']"
        c.install('nova-controller')
        #        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        #        self.assertTrue('running' in stdout)

        pass

class NovaVncProxyConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c =configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        c.installPackages()
        c._configureNovaApi()
        c = configuration.NovaVncProxyConfig()
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.NovaVncProxyConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.NovaVncProxyConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-VNCPROXY configruration
        c.vncproxy_host = c.my_ip
        c.vncproxy_port = '6080'
        c.vncproxy_type = 'http'

        c._configureNovaVncProxy()
        #        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        #        self.assertTrue('running' in stdout)

        pass

class NovaSchedulerConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c = configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        result = c.installPackages()
        c._configureNovaApi()

        c = configuration.NovaSchedulerConfig()
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.NovaSchedulerConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.NovaSchedulerConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-SCHEDULER configruration
        c.scheduler_max_cores = '16'
        c.scheduler_max_gigabytes = '2048'
        c.scheduler_max_networks = '1000'
        c.scheduler_driver = 'nova.scheduler.simple.SimpleScheduler'

        c._configureNovaScheduler()
        #        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        #        self.assertTrue('running' in stdout)

        pass

class NovaVolumeLVMLinuxConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c = configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        result = c.installPackages()
        c._configureNovaApi()

        c = configuration.NovaVolumeLinuxLVMConfig()
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.NovaVolumeLinuxLVMConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.NovaVolumeLinuxLVMConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-VOLUME configruration
        c.lvm_device = '/dev/sdb'
        c.use_local_volumes = 'true'

        c._configureNovaVolumeLinuxLVM()
        #        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        #        self.assertTrue('running' in stdout)

        pass

class NovaComputeConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c = configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        result = c.installPackages()
        c._configureNovaApi()

        c = configuration.NovaSchedulerConfig()
        result = c.installPackages()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-SCHEDULER configruration
        c.scheduler_max_cores = '16'
        c.scheduler_max_gigabytes = '2048'
        c.scheduler_max_networks = '1000'
        c.scheduler_driver = 'nova.scheduler.simple.SimpleScheduler'

        c._configureNovaScheduler()
        pass

    def tearDown(self):
        c =configuration.NovaComputeConfig()
        c.use_iscsi = False
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaSchedulerConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.NovaComputeConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # NOVA-VNCPROXY configruration
        c.vncproxy_host = '127.0.0.1'
        c.vncproxy_port = '6080'
        c.vncproxy_type = 'http'

        # NOVA-COMPUTE KVM specific
        c.libvirt_type = 'qemu'

        # ISCSI connectivity
        c.iscsi_ip_prefix = '192.168.10.32'
        c.num_targets = '100'
        c.storage_hostname = 'nova-volume'

        # Network interfaces
        c.iface_list = c._operatingsystem.getNetworkConfiguration()
        c.management_interface = 'eth0'
        for iface in c.iface_list:
            if iface['name'] == c.management_interface:
                c.my_ip = iface['address']

        c.flat_interface = 'eth1'

        # Connect to shared filesystem
        c.instances_path = '/var/lib/nova/instances'
        c.instances_filesystem_mount_type = 'local'
        c.mount_point = None
        c.mount_parameters = None

        # NOVA-VOLUME QEMU Specific
        c.use_volume_nfs = False
        c.volume_driver = 'nova.volume.driver.ISCSIDriver'

        # Boot behaviour and virtio
        c.resume_guests_state_on_host_boot = 'true'
        c.start_guests_on_host_boot = 'false'
        c.libvirt_use_virtio_for_bridges = 'false'

        c.hugepages = False
        c.hugepages_percentage = '100'

        c.minimum_root_size = '1'

        c.use_iscsi = False
        c.install('nova-controller')
        #        (stdout, stderr) = utils.execute("service rabbitmq-server status")
        #        self.assertTrue('running' in stdout)

        pass


class NovaNetworkConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c = configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        result = c.installPackages()
        c._configureNovaApi()

        c = configuration.NovaSchedulerConfig()
        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-SCHEDULER configruration
        c.scheduler_max_cores = '16'
        c.scheduler_max_gigabytes = '2048'
        c.scheduler_max_networks = '1000'
        c.scheduler_driver = 'nova.scheduler.simple.SimpleScheduler'

        result = c.installPackages()
        c._configureNovaScheduler()

        c = configuration.NovaNetworkConfig()
        c.public_ip = '192.168.10.64'
        c.public_ip_mask = '255.255.255.255'
        c.public_ip_gateway = '192.168.10.1'
        c.firewall_public_ip = True
        result = c.installPackages()
        pass

    def tearDown(self):
        c =configuration.NovaNetworkConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaSchedulerConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.NovaNetworkConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-NETWORK SPECIFIC
        c.dhcpbridge = '/usr/bin/nova-dhcpbridge'
        c.dhcpbridge_flagfile = '/etc/nova/nova-network-stackops.conf'
        c.routing_source_ip = '192.168.10.64'
        c.floating_range = '192.168.10.64/28'

        # Default Fixed range configuration
        c.network_manager = 'nova.network.manager.FlatDHCPManager'
        c.fixed_range = '10.0.0.0/8'
        c.network_size = '256'
        c.network_number = '1'
        c.vlanstart = '100'
        c.bridge = 'br100'
        c.dns1 = '8.8.8.8'
        c.dns2 = '8.8.4.4'

        # Interfaces configuration
        c.flat_interface = 'dummy0'
        c.public_interface = 'eth0'
        c.management_interface = 'eth0'
        c.bridged_interface = c.flat_interface
        iface_list = c._operatingsystem.getNetworkConfiguration()
        for iface in iface_list:
            if iface['name'] == c.management_interface:
                c.my_ip = iface['address']
            if c.routing_source_ip is None:
                if iface['name'] == c.public_interface:
                    c.routing_source_ip = iface['address']

        c.public_ip = '192.168.10.64'
        c.public_ip_mask = '255.255.255.255'
        c.public_ip_gateway = '192.168.10.1'
        c.firewall_public_ip = True

        octets = c.fixed_range.split('/')[0].split('.')
        c.flat_network_dhcp_start = '%s.%s.%s.%i' % (octets[0], octets[1], octets[2], int(octets[3]) + 2)

        result = c.install(hostname='nova-controller')
        print result
        self.assertFalse(len(result)>0)
        pass

class HorizonConfigTest(unittest.TestCase):

    def _uninstallMySQLServer(self):
        utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
        utils.execute("apt-get -y autoremove", check_exit_code=False)

    def setUp(self):
        log.startLogging(sys.stdout)
        c = configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        result = c.installPackages()

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_drop_schema = True

        # GLANCE database configuration
        c.glance_username = "glance"
        c.glance_password = "stackops"
        c.glance_schema = "glance"
        c.glance_drop_schema = True

        # KEYSTONE database configuration
        c.keystone_username = "keystone"
        c.keystone_password = "stackops"
        c.keystone_schema = "keystone"
        c.keystone_drop_schema = True

        # GLANCE database configuration
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_mount_type = 'local'

        c._configureMySQL()
        c = configuration.RabbitMQMasterConfig()
        result = c.installPackages()
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        c.keystone_username = 'keystone'
        c.keystone_password = 'stackops'
        c.keystone_host = '127.0.0.1'
        c.keystone_port = '3306'
        c.keystone_schema = 'keystone'
        c.keystone_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (c.keystone_username, c.keystone_password, c.keystone_host, c.keystone_port,c.keystone_schema)
        c.admin_password = 'password'
        c.default_password = 'password'
        c.default_username = ''
        c.default_tenant = ''
        c.endpoint = 'http://localhost:35357/v2.0'
        c._configureKeystone()
        c = configuration.GlanceConfig()
        c.glance_mount_type = 'local'
        result = c.installPackages()
        c.glance_username = 'glance'
        c.glance_password = 'stackops'
        c.glance_host = '127.0.0.1'
        c.glance_port = '3306'
        c.glance_schema = 'glance'
        c.glance_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (c.glance_username, c.glance_password, c.glance_host, c.glance_port, c.glance_schema)
        c.glance_mount_type = 'local'
        c.admin_password = 'password'
        c._configureGlance()
        c = configuration.NovaApiConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # EC2 API Configuration
        c.ec2_hostname = '127.0.0.1'
        c.ec2_dmz = '127.0.0.1'
        c.ec2_port = '8773'

        # Openstack API Configuration
        c.osapi_port = '8774'

        # S3 API configuration
        c.s3_hostname = '127.0.0.1'
        c.s3_dmz = '127.0.0.1'
        c.s3_port = '3333'

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # KEYSTONE Service configuration
        c.keystone_host = '127.0.0.1'
        c.keystone_user_port = '5000'
        c.keystone_admin_port = '32357'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # api paste configuration
        c.api_paste_config = '/etc/nova/api-paste.ini'

        # Enable admin API extensions
        c.allow_admin_api = 'true'

        # keystone admin password
        c.admin_password = 'password'

        # Quotas
        c.quota_instances = '4096'
        c.quota_cores = '8192'
        c.quota_ram = str(1024 * 1024 * 20)
        c.quota_volumes = '8192'
        c.quota_gigabytes = str(1024 * 20)
        c.quota_floating_ips = '254'
        c.quota_metadata_items = '128'
        c.quota_max_injected_files = '5'
        c.quota_max_injected_file_content_bytes = str(10 * 1024)
        c.quota_max_injected_file_path_bytes = '255'

        c.set_flavors = True
        c.flavors_list = "['tiny;512;1;0;999','small;1024;1;10;1000','medium;2048;2;20;1001','large;4096;4;40;1002']"
        result = c.installPackages()
        c.install('nova-controller')

        c =configuration.NovaVncProxyConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-VNCPROXY configruration
        c.vncproxy_host = c.my_ip
        c.vncproxy_port = '6080'
        c.vncproxy_type = 'http'

        c.installPackages()
        c._configureNovaVncProxy()

        c = configuration.NovaSchedulerConfig()
        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-SCHEDULER configruration
        c.scheduler_max_cores = '16'
        c.scheduler_max_gigabytes = '2048'
        c.scheduler_max_networks = '1000'
        c.scheduler_driver = 'nova.scheduler.simple.SimpleScheduler'

        result = c.installPackages()
        c._configureNovaScheduler()

        c = configuration.NovaVolumeLinuxLVMConfig()
        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-VOLUME configruration
        c.lvm_device = '/dev/sdb'
        c.use_local_volumes = 'true'

        result = c.installPackages()
        c.install('nova-controller')

        c = configuration.NovaNetworkConfig()
        c.public_ip = '192.168.10.64'
        c.public_ip_mask = '255.255.255.255'
        c.public_ip_gateway = '192.168.10.1'
        c.firewall_public_ip = True
        result = c.installPackages()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # NOVA-NETWORK SPECIFIC
        c.dhcpbridge = '/usr/bin/nova-dhcpbridge'
        c.dhcpbridge_flagfile = '/etc/nova/nova-network-stackops.conf'
        c.routing_source_ip = '192.168.10.64'
        c.floating_range = '192.168.10.64/28'

        # Default Fixed range configuration
        c.network_manager = 'nova.network.manager.FlatDHCPManager'
        c.fixed_range = '10.0.0.0/8'
        c.network_size = '256'
        c.network_number = '1'
        c.vlanstart = '100'
        c.bridge = 'br100'
        c.dns1 = '8.8.8.8'
        c.dns2 = '8.8.4.4'

        # Interfaces configuration
        c.flat_interface = 'dummy0'
        c.public_interface = 'eth0'
        c.management_interface = 'eth0'
        c.bridged_interface = c.flat_interface
        iface_list = c._operatingsystem.getNetworkConfiguration()
        for iface in iface_list:
            if iface['name'] == c.management_interface:
                c.my_ip = iface['address']
            if c.routing_source_ip is None:
                if iface['name'] == c.public_interface:
                    c.routing_source_ip = iface['address']

        c.public_ip = '192.168.10.64'
        c.public_ip_mask = '255.255.255.255'
        c.public_ip_gateway = '192.168.10.1'
        c.firewall_public_ip = False

        octets = c.fixed_range.split('/')[0].split('.')
        c.flat_network_dhcp_start = '%s.%s.%s.%i' % (octets[0], octets[1], octets[2], int(octets[3]) + 2)

        result = c.install(hostname='nova-controller')

        c =configuration.NovaComputeConfig()

        # Basic common parameters
        c.verbose = 'true'
        c.nodaemon = 'true'
        c.auth_driver = 'nova.auth.dbdriver.DbDriver'
        c.use_project_ca = 'true'
        c.logdir = '/var/log/nova'
        c.state_path = '/var/lib/nova'
        c.lock_path = '/var/lock/nova'

        # NOVA database configuration
        c.nova_username = "nova"
        c.nova_password = "stackops"
        c.nova_schema = "nova"
        c.nova_host = '127.0.0.1'
        c.nova_port = '3306'
        c.nova_charset = 'utf8'
        c.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s?charset=%s' % (
            c.nova_username, c.nova_password, c.nova_host, c.nova_port, c.nova_schema, c.nova_charset)

        # RabbitMQ configuration
        c.rabbit_host = '127.0.0.1'

        # My IP
        management_interface = 'eth0'
        c.my_ip = c.whatIsMyIp(management_interface)

        # GLANCE Service configuration
        c.glance_hostname = '127.0.0.1'
        c.glance_port = '9292'
        c.image_service = 'nova.image.glance.GlanceImageService'

        # NOVA-VNCPROXY configruration
        c.vncproxy_host = '192.168.10.32'
        c.vncproxy_port = '6080'
        c.vncproxy_type = 'http'

        # NOVA-COMPUTE KVM specific
        c.libvirt_type = 'qemu'

        # ISCSI connectivity
        c.iscsi_ip_prefix = '192.168.10.32'
        c.num_targets = '100'
        c.storage_hostname = 'nova-volume'

        # Network interfaces
        c.iface_list = c._operatingsystem.getNetworkConfiguration()
        c.management_interface = 'eth0'
        for iface in c.iface_list:
            if iface['name'] == c.management_interface:
                c.my_ip = iface['address']

        c.flat_interface = 'eth1'

        # Connect to shared filesystem
        c.instances_path = '/var/lib/nova/instances'
        c.instances_filesystem_mount_type = 'local'
        c.mount_point = None
        c.mount_parameters = None

        # NOVA-VOLUME QEMU Specific
        c.use_volume_nfs = False
        c.volume_driver = 'nova.volume.driver.ISCSIDriver'

        # Boot behaviour and virtio
        c.resume_guests_state_on_host_boot = 'true'
        c.start_guests_on_host_boot = 'false'
        c.libvirt_use_virtio_for_bridges = 'false'

        c.hugepages = False
        c.hugepages_percentage = '100'

        c.minimum_root_size = '1'

        c.use_iscsi = True

        c.installPackages()
        c.install('nova-controller')

        pass

    def tearDown(self):
        c =configuration.HorizonConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaComputeConfig()
        c.use_iscsi = True
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaNetworkConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaSchedulerConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaVolumeLinuxLVMConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaVncProxyConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.NovaApiConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.GlanceConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.KeystoneConfig()
        c.uninstall(hostname='nova-controller')
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='nova-controller')
        self._uninstallMySQLServer()
        pass

    def testConfigure(self):
        c =configuration.HorizonConfig()
        result = c.install(hostname='nova-controller')
        print result
        self.assertFalse(len(result)>0)
        pass

class FullConfigTest(HorizonConfigTest):
    def tearDown(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
