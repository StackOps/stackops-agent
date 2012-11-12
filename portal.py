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

class PortalConfig(Config):
    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file

    def write(self, xmldoc):
        # Basic Portal
        # PORTAL database configuration
        self.portal_username = self._filler.getPropertyValue(xmldoc, 'portal_database', 'username', 'portal')
        self.portal_password = self._filler.getPropertyValue(xmldoc, 'portal_database', 'password', 'portal')
        self.portal_schema = self._filler.getPropertyValue(xmldoc, 'portal_database', 'schema', 'portal')
        self.portal_host = self._filler.getPropertyValue(xmldoc, 'portal_database', 'host', '127.0.0.1')
        self.portal_port = self._filler.getPropertyValue(xmldoc, 'portal_database', 'port', '3306')

        self.ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname', '127.0.0.1')
        # KEYSTONE Service configuration
        self.keystone_host = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_host', self.ec2_hostname)
        self.keystone_user_port = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_user_port', '5000')
        self.keystone_admin_port = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_admin_port', '32357')
        self.endpoint = 'http://%s:%s/v2.0' % (self.keystone_host, self.keystone_admin_port)

        # Keystone admin password
        self.admin_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'admin_password', 'password')

        self.horizon_host = self._filler.getPropertyValue(xmldoc, 'horizon', 'host')
        if self.horizon_host==None or len(self.horizon_host)==0:
            self.horizon_host = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip')
            if self.horizon_host==None or len(self.horizon_host)==0:
                self.horizon_host = self.ec2_hostname
        return

    def _configurePortal(self):
        # Do nothing (security here????)
        # Database config
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "CREATE TABLE PORTAL_SETTINGS (ID bigint(20) NOT NULL AUTO_INCREMENT, PROPERTY_KEE varchar(255) NOT NULL, PROPERTY_VALUE varchar(255) NOT NULL, PRIMARY KEY (ID))"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "CREATE TABLE PORTAL_SYSTEM_CHECK (ID bigint(20) NOT NULL AUTO_INCREMENT,CHECK_NAME varchar(255) NOT NULL,CHECKER_CLASS varchar(255) NOT NULL,SYSTEM_NAME varchar(255) NOT NULL,PRIMARY KEY (ID))"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SYSTEM_CHECK values (1, 'Identity service check', 'com.stackops.portal.service.checks.KeystoneBuiltinCheck', 'Keystone')"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS values (2, 'identity.admin.token', '%s')"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema, self.admin_password))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS values (3, 'auth.username', 'portal')"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS values (4, 'auth.password', '%s')"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema, self.admin_password))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS values (5, 'identity.endpoint.publicURL', 'http://%s:35357/v2.0')"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema, self.keystone_host))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS values (6, 'identity.endpoint.adminURL', 'http://%s:35357/v2.0')"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema, self.keystone_host))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS values (7, 'check.identity.endpoint', 'http://%s:35357');"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema, self.keystone_host))
        utils.execute(
            '''mysql -h%s --port=%s -u%s --password=%s --database=%s -e "insert into PORTAL_SETTINGS (property_kee,property_value) values ('mode','release');"''' % (
                self.portal_host, self.portal_port, self.portal_username, self.portal_password, self.portal_schema))

        # JVM configuration
        utils.execute('sed -i /JAVA_OPTS/d /etc/default/tomcat7')
        utils.execute('''echo 'JAVA_OPTS="-Djava.awt.headless=true -Xmx768m -XX:+UseConcMarkSweepGC -Dhibernate.connection.password=%s"' >> /etc/default/tomcat7''' % self.portal_password)
        utils.execute('''echo 'HORIZON_HOST=%s' >> /etc/default/tomcat7''' % self.horizon_host)
        utils.execute('service tomcat7 stop', check_exit_code=False)
        utils.execute('service tomcat7 start')
        return


    def install(self, hostname):
        """
        Install all stuff needed to run Portal for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configurePortal()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        Portal uninstall process
        """
        utils.execute("apt-get -y --purge remove openjdk-7-jdk tomcat7", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('openjdk-7-jdk tomcat7 stackops-portal stackops-documentation-portal-plugin stackops-horizon-portal-plugin openstack-clis-portal-plugin stackops-blog-portal-plugin stackops-chat-portal-plugin stackops-forum-portal-plugin stackops-products-portal-plugin', interactive=False)
        return