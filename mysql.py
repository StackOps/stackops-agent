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

import utils

from configuration import Config

class MySQLMasterConfig(Config):
    def __init__(self):
        """
        Constructor
        """

    # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # Basic Infrastructure Services
        self.install_mysql = self._filler.getPropertyValue(xmldoc, 'infrastructure', 'install_mysql', 'true') == 'true'
        self.mysql_root_password = self._filler.getPropertyValue(xmldoc, 'infrastructure', 'mysql_password', 'stackops')

        # NOVA database configuration
        self.nova_username = self._filler.getPropertyValue(xmldoc, 'database', 'username', 'nova')
        self.nova_password = self._filler.getPropertyValue(xmldoc, 'database', 'password', 'nova')
        self.nova_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema', 'nova')
        self.nova_drop_schema = self._filler.getPropertyValue(xmldoc, 'database', 'dropschema', 'true') == 'true'

        # GLANCE database configuration
        self.glance_username = self._filler.getPropertyValue(xmldoc, 'glance_database', 'username', 'glance')
        self.glance_password = self._filler.getPropertyValue(xmldoc, 'glance_database', 'password', 'nova')
        self.glance_schema = self._filler.getPropertyValue(xmldoc, 'glance_database', 'schema', 'glance')
        self.glance_drop_schema = self._filler.getPropertyValue(xmldoc, 'glance_database', 'dropschema',
            'true') == 'true'

        # KEYSTONE database configuration
        self.keystone_username = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'username', 'keystone')
        self.keystone_password = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'password', 'nova')
        self.keystone_schema = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'schema', 'keystone')
        self.keystone_drop_schema = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'dropschema',
            'true') == 'true'

        # PORTAL database configuration
        self.portal_username = self._filler.getPropertyValue(xmldoc, 'portal_database', 'username', 'portal')
        self.portal_password = self._filler.getPropertyValue(xmldoc, 'portal_database', 'password', 'portal')
        self.portal_schema = self._filler.getPropertyValue(xmldoc, 'portal_database', 'schema', 'portal')
        self.portal_drop_schema = self._filler.getPropertyValue(xmldoc, 'portal_database', 'dropschema',
            'true') == 'true'

        return

    def _configureMySQL(self):
        utils.execute("sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf")
        utils.execute('service mysql restart')
        if self.nova_drop_schema:
            utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS nova;"' % self.mysql_root_password,
                check_exit_code=False)
        if self.glance_drop_schema:
            utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS glance;"' % self.mysql_root_password,
                check_exit_code=False)
        if self.keystone_drop_schema:
            utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS keystone;"' % self.mysql_root_password,
                check_exit_code=False)
        if self.portal_drop_schema:
            utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS portal;"' % self.mysql_root_password,
                check_exit_code=False)
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s default character set utf8;"' % (self.mysql_root_password, self.nova_schema))
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s default character set utf8;"' % (self.mysql_root_password, self.glance_schema))
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s default character set utf8;"' % (self.mysql_root_password, self.keystone_schema))
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s default character set utf8;"' % (self.mysql_root_password, self.portal_schema))

        utils.execute(
            '''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s';"''' % (
                self.mysql_root_password, self.portal_schema, self.portal_username, self.portal_password))
        utils.execute('''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s';"''' % (
            self.mysql_root_password, self.portal_schema, self.portal_username, self.portal_password))
        if self.nova_username == 'root' and self.glance_username == 'root' and self.keystone_username == 'root':
            utils.execute(
                '''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%%' IDENTIFIED BY '%s';"''' % (
                    self.mysql_root_password, self.mysql_root_password))
        else:
            utils.execute(
                '''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s';"''' % (
                    self.mysql_root_password, self.nova_schema, self.nova_username, self.nova_password))
            utils.execute(
                '''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s';"''' % (
                    self.mysql_root_password, self.glance_schema, self.glance_username, self.glance_password))
            utils.execute(
                '''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s';"''' % (
                    self.mysql_root_password, self.keystone_schema, self.keystone_username, self.keystone_password))
            utils.execute('''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s';"''' % (
                self.mysql_root_password, self.nova_schema, self.nova_username, self.nova_password))
            utils.execute('''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s';"''' % (
                self.mysql_root_password, self.glance_schema, self.glance_username, self.glance_password))
            utils.execute('''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s';"''' % (
                self.mysql_root_password, self.keystone_schema, self.keystone_username, self.keystone_password))

    def install(self, hostname):
        """
        Install all stuff needed to run a mysql database for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureMySQL()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        MySQL database cannot be uninstalled.
        """
        raise NotImplementedError("MySQL Database cannot be uninstalled.")

    def installPackages(self):
        self.installPackagesCommon()
        utils.execute(
            'echo mysql-server-5.5 mysql-server/root_password password ' + self.mysql_root_password + ' | debconf-set-selections')
        utils.execute(
            'echo mysql-server-5.5 mysql-server/root_password_again password ' + self.mysql_root_password + ' | debconf-set-selections')
        utils.execute('echo mysql-server-5.5 mysql-server/start_on_boot boolean true')
        self._installDeb('mysql-server python-mysqldb')
