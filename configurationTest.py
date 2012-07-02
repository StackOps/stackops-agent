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
	utils.execute("apt-get -y remove mysql-server python-mysqldb", check_exit_code=False)
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
        c.uninstall(hostname='stackops-node')
        pass
    def tearDown(self):
        c =configuration.RabbitMQMasterConfig()
        c.uninstall(hostname='stackops-node')
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
        c = configuration.KeystoneConfig()
        result = c.installPackages()
        pass

    def tearDown(self):
#        c =configuration.KeystoneConfig()
#        c.uninstall(hostname='stackops-node')
#        c =configuration.RabbitMQMasterConfig()
#        c.uninstall(hostname='stackops-node')
#        self._uninstallMySQLServer()
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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
