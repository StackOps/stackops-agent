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
Created on Feb 21, 2011

@author: Diego Parrilla
"""
import getpass

import flags
import install
import utils
import os, os.path
import shutil
import re
import time
import base64
from twisted.python import log

class VanillaConfig(object):
    '''
    classdocs
    '''

    _DEBUG = True
    _filename = "nofilename"

    _flags = flags.Flags()
    _filler = install.Filler()
    _operatingsystem = install.OperatingSystem()

    def __init__(self):
        """
        Constructor
        """

    def _readFile(self, filename):
        return self._flags.readFile("/etc/nova", filename)

    def _writeFile(self, filename, parameters):
        self._flags.writeFile("/etc/nova", filename, parameters)

    def readXML(self):
        raise NotImplementedError("Should have implemented this")

    def writeXML(self):
        raise NotImplementedError("Should have implemented this")

    def install(self, hostname):
        raise NotImplementedError("Should have implemented this")

    def uninstall(self, hostname):
        raise NotImplementedError("Should have implemented this")

    def write(self, xmldoc):
        raise NotImplementedError("Should have implemented this")

    def _installDeb(self, name, interactive=True):
        if (interactive):
            utils.execute('apt-get -y install %s' % name)
        else:
            utils.execute('DEBIAN_FRONTEND=noninteractive apt-get -y install %s' % name)

    def installPackages(self):
        raise NotImplementedError("Should have implemented this")


class Config(VanillaConfig):
    '''
    classdocs
    '''

    def installPackagesCommon(self):
        #        self._installDeb('collectd-core')
        #        self._installDeb('snmp')
        #        self._installDeb('snmpd')
        print


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
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s;"' % (self.mysql_root_password, self.nova_schema))
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s;"' % (self.mysql_root_password, self.glance_schema))
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE %s;"' % (self.mysql_root_password, self.keystone_schema))

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


class RabbitMQMasterConfig(Config):
    def __init__(self):
        """
        Constructor
        """

        # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # Basic Infrastructure Services
        self.install_rabbitmq = self._filler.getPropertyValue(xmldoc, 'infrastructure', 'install_rabbitmq',
            'true') == 'true'
        return

    def _configureRabbitMQ(self):
        # Do nothing (security here????)
        return


    def install(self, hostname):
        """
        Install all stuff needed to run RabbitMQ for Nova
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureRabbitMQ()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        RabbitMQ uninstall process
        """
        utils.execute("apt-get -y --purge remove rabbitmq-server memcached python-memcache", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('rabbitmq-server memcached python-memcache', interactive=False)
        return


class KeystoneConfig(Config):
    def __init__(self):
        """
        Constructor
        """

    # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # keystone is always used. Flag kept for backwards compatibility
        self.use_keystone = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_enabled', 'true') == 'true'
        self.keystone_username = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'username', 'keystone')
        self.keystone_password = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'password', 'nova')
        self.keystone_host = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'host', '127.0.0.1')
        self.keystone_port = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'port', '3306')
        self.keystone_schema = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'schema', 'keystone')
        self.keystone_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (
            self.keystone_username, self.keystone_password, self.keystone_host, self.keystone_port,
            self.keystone_schema)
        self.admin_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'admin_password', 'password')
        self.default_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'default_password',
            'password')
        self.default_username = self._filler.getPropertyValue(xmldoc, 'auth_users', 'default_username', '')
        self.default_tenant = self._filler.getPropertyValue(xmldoc, 'auth_users', 'default_tenant', '')
        self.endpoint = 'http://localhost:35357/v2.0'
        return

    def get_id(self, str):
        (stdout, stderr) = utils.execute("echo '%s' | awk '/ id / { print $4 }'" % str)
        return stdout.replace('\n', '')

    def _configureKeystone(self):
        utils.execute(
            "sed -i 's/admin_token = ADMIN/admin_token = %s/g' /etc/keystone/keystone.conf" % self.admin_password)
        utils.execute(
            "sed -i 's#connection = sqlite:////var/lib/keystone/keystone.db#connection = %s#g' /etc/keystone/keystone.conf" % self.keystone_sql_connection)
        utils.execute(
            "sed -i 's#driver = keystone.catalog.backends.sql.Catalog#driver = keystone.catalog.backends.templated.TemplatedCatalog\\ntemplate_file = /etc/keystone/default_catalog.templates#g' /etc/keystone/keystone.conf")
        utils.execute("service keystone restart")
        utils.execute("keystone-manage db_sync")
        # Configure service users/roles
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s tenant-create --name=admin' % (self.endpoint, self.admin_password))
        admin_tenant = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s tenant-create --name=service' % (self.endpoint, self.admin_password))
        service_tenant = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-create --name=admin --pass=%s --email=admin@domain.com' % (
            self.endpoint, self.admin_password, self.admin_password))
        admin_user = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-create --name=nova --pass=%s --tenant_id %s --email=nova@domain.com' % (
            self.endpoint, self.admin_password, self.admin_password, service_tenant))
        nova_user = self.get_id(stdout)

        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-create --name=glance --pass=%s --tenant_id %s --email=glance@domain.com' % (
            self.endpoint, self.admin_password, self.admin_password, service_tenant))
        glance_user = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=admin' % (self.endpoint, self.admin_password))
        admin_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=KeystoneAdmin' % (self.endpoint, self.admin_password))
        keystone_admin_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=KeystoneServiceAdmin' % (self.endpoint, self.admin_password))
        keystone_service_admin_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=Member' % (self.endpoint, self.admin_password))
        member_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
            self.endpoint, self.admin_password, admin_user, admin_role, admin_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
            self.endpoint, self.admin_password, admin_user, keystone_admin_role, admin_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
            self.endpoint, self.admin_password, admin_user, keystone_service_admin_role, admin_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
            self.endpoint, self.admin_password, nova_user, admin_role, service_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
            self.endpoint, self.admin_password, glance_user, admin_role, service_tenant))
        return


    def install(self, hostname):
        """
        Install all stuff needed to run Keystone
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureKeystone()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result


    def uninstall(self, hostname):
        """
        Keystone uninstall process
        """
        utils.execute("apt-get -y --purge remove keystone python-keystone python-keystoneclient python-mysqldb",
            check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return


    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('keystone python-keystone python-keystoneclient python-mysqldb')
        return


class GlanceConfig(Config):
    def __init__(self):
        """
        Constructor
        """

    # Write the parameters (if possible) from the xml file
    def write(self, xmldoc):
        # Keystone admin password
        self.admin_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'admin_password', 'password')
        # GLANCE database configuration
        self.glance_username = self._filler.getPropertyValue(xmldoc, 'glance_database', 'username', 'glance')
        self.glance_password = self._filler.getPropertyValue(xmldoc, 'glance_database', 'password', 'nova')
        self.glance_host = self._filler.getPropertyValue(xmldoc, 'glance_database', 'host', '127.0.0.1')
        self.glance_port = self._filler.getPropertyValue(xmldoc, 'glance_database', 'port', '3306')
        self.glance_schema = self._filler.getPropertyValue(xmldoc, 'glance_database', 'schema', 'glance')
        self.glance_drop_schema = self._filler.getPropertyValue(xmldoc, 'glance_database', 'dropschema',
            'true') == 'true'
        self.glance_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (
            self.glance_username, self.glance_password, self.glance_host, self.glance_port, self.glance_schema)
        return

    def _configureGlance(self):
        utils.execute(
            "sed -i 's/%%SERVICE_PASSWORD%%/%s/g' /etc/glance/glance-api-paste.ini" % self.admin_password)
        utils.execute(
            "sed -i 's/%%SERVICE_PASSWORD%%/%s/g' /etc/glance/glance-registry-paste.ini" % self.admin_password)
        utils.execute(
            "sed -i 's/%%SERVICE_TENANT_NAME%%/admin/g' /etc/glance/glance-api-paste.ini")
        utils.execute(
            "sed -i 's/%%SERVICE_TENANT_NAME%%/admin/g' /etc/glance/glance-registry-paste.ini")
        utils.execute(
            "sed -i 's/%%SERVICE_USER%%/admin/g' /etc/glance/glance-api-paste.ini")
        utils.execute(
            "sed -i 's/%%SERVICE_USER%%/admin/g' /etc/glance/glance-registry-paste.ini")
        utils.execute(
            "sed -i 's#sql_connection = sqlite:////var/lib/glance/glance.sqlite#connection = %s#g' /etc/glance/glance-registry.conf" % self.glance_sql_connection)
        utils.execute('sed -i "/[paste_deploy]/d" /etc/glance/glance-registry.conf')
        utils.execute('echo "[paste_deploy]" >> /etc/glance/glance-registry.conf')
        utils.execute('sed -i "/flavor = keystone/d" /etc/glance/glance-registry.conf')
        utils.execute('echo "flavor = keystone" >> /etc/glance/glance-registry.conf')
        utils.execute('sed -i "/[paste_deploy]/d" /etc/glance/glance-api.conf')
        utils.execute('echo "[paste_deploy]" >> /etc/glance/glance-api.conf')
        utils.execute('sed -i "/flavor = keystone/d" /etc/glance/glance-api.conf')
        utils.execute('echo "flavor = keystone" >> /etc/glance/glance-api.conf')
        utils.execute("glance-manage version_control 0")
        utils.execute("glance-manage db_sync")
        utils.execute("service glance-api restart && service glance-registry restart")
        return


    def install(self, hostname):
        """
        Install all stuff needed to run Keystone
        """
        result = ''
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                self._configureGlance()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        Keystone uninstall process
        """
        utils.execute("apt-get -y --purge remove glance glance-api glance-client glance-common glance-registry python-mysqldb",
            check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        return

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('glance glance-api glance-client glance-common glance-registry python-mysqldb')
        return


class ControllerConfig(Config):
    '''
    classdocs
    '''

    _filename = "nova-controller.conf"
    TOKEN_SIZE = 12
    TOKEN = None

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

        # Basic Infrastructure Services
        self.install_mysql = self._filler.getPropertyValue(xmldoc, 'infrastructure', 'install_mysql', 'true') == 'true'
        self.install_rabbitmq = self._filler.getPropertyValue(xmldoc, 'infrastructure', 'install_rabbitmq',
            'true') == 'true'
        self.mysql_root_password = self._filler.getPropertyValue(xmldoc, 'infrastructure', 'mysql_password', 'nova')

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

        # GLANCE database configuration
        self.glance_username = self._filler.getPropertyValue(xmldoc, 'glance_database', 'username', 'root')
        self.glance_password = self._filler.getPropertyValue(xmldoc, 'glance_database', 'password', 'nova')
        self.glance_host = self._filler.getPropertyValue(xmldoc, 'glance_database', 'host', '127.0.0.1')
        self.glance_port = self._filler.getPropertyValue(xmldoc, 'glance_database', 'port', '3306')
        self.glance_schema = self._filler.getPropertyValue(xmldoc, 'glance_database', 'schema', 'nova')
        self.glance_drop_schema = self._filler.getPropertyValue(xmldoc, 'glance_database', 'dropschema',
            'true') == 'true'
        self.glance_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (
            self.glance_username, self.glance_password, self.glance_host, self.glance_port, self.glance_schema)

        # EC2 API Configuration
        self.ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname', '127.0.0.1')
        self.ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz', '127.0.0.1')
        self.ec2_port = self._filler.getPropertyValue(xmldoc, 'ec2', 'port', '80')
        self.ec2_dmz_port = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz_port', '8773') # TODO

        # Openstack API Configuration
        self.osapi_hostname = self._filler.getPropertyValue(xmldoc, 'osapi', 'hostname', self.ec2_hostname)
        self.osapi_dmz = self._filler.getPropertyValue(xmldoc, 'osapi', 'dmz', self.ec2_dmz) # TODO
        self.osapi_port = self._filler.getPropertyValue(xmldoc, 'osapi', 'port', '80')
        self.osapi_dmz_port = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz_port', '8774') # TODO

        # S3 API configuration
        self.s3_hostname = self._filler.getPropertyValue(xmldoc, 's3', 'hostname', self.ec2_hostname)
        self.s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz', self.ec2_dmz)
        self.s3_port = self._filler.getPropertyValue(xmldoc, 's3', 'port', '80')
        self.s3_dmz_port = self._filler.getPropertyValue(xmldoc, 's3', 'port', '3333') # TODO

        # GLANCE Service configuration
        self.glance_hostname = self._filler.getPropertyValue(xmldoc, 'glance', 'hostname', self.ec2_hostname)
        self.glance_port = self._filler.getPropertyValue(xmldoc, 'glance', 'port', '9292')
        self.image_service = self._filler.getPropertyValue(xmldoc, 'glance', 'image_service',
            'nova.image.glance.GlanceImageService')
        self.glance_mount_type = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_type', 'local')
        if self.glance_mount_type == 'local':
            self.glance_mount_point = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_point', None)
            self.glance_mount_parameters = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_parameters', None)
        else:
            self.glance_mount_point = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_point',
                '192.168.10.198:/volumes/vol1/openstack-nfs-images')
            self.glance_mount_parameters = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_parameters',
                'rw,dev,noexec,nosuid,auto,nouser,noatime,async,rsize=8192,wsize=8192')

        # RabbitMQ configuration
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname', '127.0.0.1')

        # Scheduler configruration
        self.scheduler_max_cores = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_cores', '16')
        self.scheduler_max_gigabytes = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_gigabytes', '2048') # 2TB
        self.scheduler_max_networks = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_networks', '1000')
        self.scheduler_driver = self._filler.getPropertyValue(xmldoc, 'scheduler', 'driver',
            'nova.scheduler.simple.SimpleScheduler')

        # Keystone configuration
        self.use_keystone = self._filler.getPropertyValue(xmldoc, 'auth_users', 'keystone_enabled', 'true') == 'true'
        if not self.use_keystone:
            self.api_paste_config = 'api-paste.ini'
        else:
            self.api_paste_config = '/var/lib/keystone/examples/paste/nova-api-paste.ini'
            self.keystone_username = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'username', 'root')
            self.keystone_password = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'password', 'nova')
            self.keystone_host = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'host', '127.0.0.1')
            self.keystone_port = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'port', '3306')
            self.keystone_schema = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'schema', 'nova')
            self.keystone_drop_schema = self._filler.getPropertyValue(xmldoc, 'keystone_database', 'dropschema',
                'true') == 'true'
            self.keystone_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (
                self.keystone_username, self.keystone_password, self.keystone_host, self.keystone_port,
                self.keystone_schema)
            self.admin_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'admin_password', 'password')
            self.default_password = self._filler.getPropertyValue(xmldoc, 'auth_users', 'default_password',
                'password')
            self.default_username = self._filler.getPropertyValue(xmldoc, 'auth_users', 'default_username', '')
            self.default_tenant = self._filler.getPropertyValue(xmldoc, 'auth_users', 'default_tenant', '')

        # Configure Horizon
        self.use_horizon = self._filler.getPropertyValue(xmldoc, 'horizon', 'enabled', 'true') == 'true'

        # Flavors configuration
        self.set_flavors = self._filler.getPropertyValue(xmldoc, 'flavors', 'delete_default', 'false') == 'true'
        if self.set_flavors:
            self.flavors_list = self._filler.getPropertyValue(xmldoc, 'flavors', 'list', '[]')
        else:
            self.flavors_list = '[]'

        self.iface_list = self._operatingsystem.getNetworkConfiguration()
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        self.my_ip = '127.0.0.1'
        for iface in self.iface_list:
            if iface['name'] == self.management_interface:
                self.my_ip = iface['address']

        # VNCProxy configuration
        self.vncproxy_host = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'host', self.my_ip)
        self.vncproxy_port = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'port', '6080')
        self.vncproxy_type = self._filler.getPropertyValue(xmldoc, 'vncproxy', 'type', 'http')

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

        # Install Open VM Tools
        self.open_vm_tools = self._filler.getPropertyValue(xmldoc, 'hardening', 'open-vm-tools', 'true') == 'true'

        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'use_project_ca': self.use_project_ca,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'rabbit_host': self.rabbit_host,
                      # NOVA-CONTROLLER SPECIFIC
                      'ec2_host': self.ec2_hostname,
                      'ec2_dmz_host': self.ec2_dmz,
                      'ec2_port': self.ec2_port,
                      's3_hostname': self.s3_hostname,
                      's3_dmz': self.s3_dmz,
                      's3_port': self.s3_port,
                      'osapi_host': self.osapi_hostname,
                      'osapi_port': self.osapi_port,
                      'image_service': self.image_service,
                      'glance_api_servers': '%s:%s' % (self.glance_hostname, self.glance_port),
                      'my_ip': self.my_ip,
                      'scheduler_driver': self.scheduler_driver,
                      'max_cores': self.scheduler_max_cores,
                      'max_gigabytes': self.scheduler_max_gigabytes,
                      'max_networks': self.scheduler_max_networks,
                      'api_paste_config': self.api_paste_config,
                      'allow_admin_api': 'true',
                      'osapi_extensions_path': '/var/lib/openstackx/extensions',
                      'vncproxy_url': '%s://%s:%s' % (self.vncproxy_type, self.vncproxy_host, self.vncproxy_port),
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
        return

    def _configureMySQL(self):
        utils.execute("sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf")
        utils.execute('service mysql restart')
        if self.nova_drop_schema:
            utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS nova;"' % self.mysql_root_password,
                check_exit_code=False)
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE nova;"' % self.mysql_root_password)
        if self.glance_drop_schema:
            utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS glance;"' % self.mysql_root_password,
                check_exit_code=False)
        utils.execute('mysql -uroot -p%s -e "CREATE DATABASE glance;"' % self.mysql_root_password)
        if self.use_keystone:
            if self.keystone_drop_schema:
                utils.execute('mysql -uroot -p%s -e "DROP DATABASE IF EXISTS keystone;"' % self.mysql_root_password,
                    check_exit_code=False)
            utils.execute('mysql -uroot -p%s -e "CREATE DATABASE keystone;"' % self.mysql_root_password)
        utils.execute(
            '''mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%%' WITH GRANT OPTION;"''' % self.mysql_root_password)
        utils.execute(
            '''mysql -uroot -p%s -e "SET PASSWORD FOR 'root'@'%%' = PASSWORD('%s');"''' % (
                self.mysql_root_password, self.mysql_root_password))

    def _configCerts(self):
        utils.execute('killall dnsmasq', None, None, False)
        utils.execute('rm -fr /root/admin')
        utils.execute('mkdir /root/admin')
        utils.execute('rm -fr /root/stackops')
        utils.execute('mkdir /root/stackops')
        # stackops
        utils.execute('adduser nova --disabled-password --gecos ""', None, None, False)
        # generate new certificates
        utils.execute(
            'rm /var/lib/nova/nova/CA/cacert.pem /var/lib/nova/nova/CA/openssl.cnf /var/lib/nova/nova/CA/crl.pem', None,
            None, False)
        utils.execute('cd /var/lib/nova/nova/CA; ./genrootca.sh')
        # CA link to avoid issues with paths
        utils.execute('rm /var/lib/nova/CA', None, None, False)
        utils.execute('ln -s /var/lib/nova/nova/CA /var/lib/nova/CA')

    def _createNovaDatabase(self):
        # create the database
        utils.execute('/var/lib/nova/bin/nova-manage db sync')
        # create an admin user called 'admin'

    def _generateToken(self):
        return os.urandom(self.TOKEN_SIZE).encode("hex")

    def _deleteFlavors(self):
        # Get flavors
        (out, err) = utils.execute('/var/lib/nova/bin/nova-manage flavor list')
        old_flavors = out.split('\n')
        flavorids = []
        for str in old_flavors:
            if len(str) > 0:
                (flavorid, err) = utils.execute("echo '%s' | sed 's/: Memory:\(.*\)//g'" % str)
                flavorids.append(flavorid)
        for flavor in flavorids:
            utils.execute('/var/lib/nova/bin/nova-manage flavor delete --purge %s' % flavor)

    def _addFlavors(self):
        # Add flavors
        flavors = eval(self.flavors_list)
        for str in flavors:
            flavor = str.split(';')
            name = flavor[0]
            memory = flavor[1]
            cpu = flavor[2]
            storage = flavor[3]
            flavorid = flavor[4]
            utils.execute(
                '/var/lib/nova/bin/nova-manage flavor create --name=%s --memory=%s --cpu=%s --local_gb=%s --flavor=%s' % (
                name, memory, cpu, storage, flavorid))

    def _createDefaultProjects(self):
        # create a project called 'admin' with project manager of 'admin'
        utils.execute('/var/lib/nova/bin/nova-manage user create admin admin password')
        utils.execute('/var/lib/nova/bin/nova-manage project create admin admin')
        utils.execute('/var/lib/nova/bin/nova-manage project zipfile admin admin /root/admin/nova.zip')
        utils.execute('unzip /root/admin/nova.zip -d /root/admin')

        # create a project called 'stackops-tenant' with project manager of 'stackops'
        utils.execute('/var/lib/nova/bin/nova-manage user create stackops stackops password')
        utils.execute('/var/lib/nova/bin/nova-manage project create stackops-tenant stackops')
        utils.execute('/var/lib/nova/bin/nova-manage project zipfile stackops-tenant stackops /root/stackops/nova.zip')
        utils.execute('unzip /root/stackops/nova.zip -d /root/stackops')

    def _enableInitFiles(self):
        # enable controller components
        utils.execute('mv /etc/init/nova-ajax-console-proxy.conf.disabled /etc/init/nova-ajax-console-proxy.conf',
            check_exit_code=False)
        utils.execute('mv /etc/init/nova-api.conf.disabled /etc/init/nova-api.conf', check_exit_code=False)
        utils.execute('mv /etc/init/nova-scheduler.conf.disabled /etc/init/nova-scheduler.conf', check_exit_code=False)
        utils.execute('mv /etc/init/nova-objectstore.conf.disabled /etc/init/nova-objectstore.conf',
            check_exit_code=False)
        utils.execute('mv /etc/init/nova-vncproxy.conf.disabled /etc/init/nova-vncproxy.conf', check_exit_code=False)
        utils.execute('mv /etc/init/glance-api.conf.disabled /etc/init/glance-api.conf', check_exit_code=False)
        utils.execute('mv /etc/init/glance-registry.conf.disabled /etc/init/glance-registry.conf',
            check_exit_code=False)
        utils.execute('mv /etc/init/glance-scrubber.conf.disabled /etc/init/glance-scrubber.conf',
            check_exit_code=False)
        utils.execute('mv /etc/init/keystone.conf.disabled /etc/init/keystone.conf', check_exit_code=False)


    def _restartServices(self):
        # start controller components
        utils.execute('stop keystone; start keystone')
        utils.execute('stop glance-registry; start glance-registry')
        utils.execute('stop glance-api; start glance-api')
        utils.execute('stop glance-scrubber; start glance-scrubber')
        utils.execute('stop nova-api; start nova-api')
        utils.execute('stop nova-scheduler; start nova-scheduler')
        utils.execute('stop nova-objectstore; start nova-objectstore')
        utils.execute('stop nova-vncproxy; start nova-vncproxy')
        utils.execute('stop nova-ajax-console-proxy; start nova-ajax-console-proxy')
        utils.execute('service apache2 restart')

    def _configureNovaManage(self):
        # nova.conf in bin linked to controller info
        utils.execute('rm /var/lib/nova/bin/nova.conf', None, None, False)
        utils.execute('ln -s /etc/nova/nova-controller.conf /var/lib/nova/bin/nova.conf')

    def _configureApache(self):
        utils.execute('a2enmod proxy_http')
        utils.execute('a2enmod ssl')
        utils.execute('a2enmod rewrite')
        utils.execute('a2ensite default-ssl')
        shutil.copyfile('/var/lib/stackops/sslcert.crt', '/etc/ssl/certs/sslcert.crt')
        shutil.copyfile('/var/lib/stackops/sslcert.key', '/etc/ssl/private/sslcert.key')
        if self.use_horizon:
            shutil.copyfile('/var/lib/stackops/apache_default.conf', '/etc/apache2/sites-available/default')
            shutil.copyfile('/var/lib/stackops/apachessl_default.conf', '/etc/apache2/sites-available/default-ssl')
        else:
            shutil.copyfile('/var/lib/stackops/apache_default_no_wsgi.conf', '/etc/apache2/sites-available/default')


    def _configureGlance(self):
        if self.use_keystone:
            # link to keystone
            shutil.copyfile('/var/lib/keystone/examples/paste/glance-api.conf', '/etc/glance/glance-api.conf')
            shutil.copyfile('/var/lib/keystone/examples/paste/glance-registry.conf', '/etc/glance/glance-registry.conf')
        utils.execute('rm -fr /var/lib/glance/images', check_exit_code=False)
        utils.execute('mkdir -p /var/lib/glance/images', check_exit_code=False)
        if self.glance_mount_type == 'nfs':
            # configure NFS mount
            mpoint = '%s %s nfs %s 0 0' % (
            self.glance_mount_point, '/var/lib/glance/images', self.glance_mount_parameters)
            utils.execute("sed -i 's#%s##g' /etc/fstab" % mpoint)
            utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
            # mount NFS remote
            utils.execute('mount -a')
        utils.execute(
            "sed -i 's,sqlite:///glance.sqlite,%s,g' /etc/glance/glance-registry.conf" % self.glance_sql_connection)
        utils.execute(
            "sed -i 's,sqlite:////var/lib/glance/glance.sqlite,%s,g' /etc/glance/glance-scrubber.conf" % self.glance_sql_connection)
        utils.execute("sed -i 's@daemon = False@daemon = True@g' /etc/glance/glance-scrubber.conf")
        utils.execute("sed -i 's/999888777666/%s/g' /etc/glance/glance-api.conf" % self.TOKEN)
        utils.execute("sed -i 's/999888777666/%s/g' /etc/glance/glance-registry.conf" % self.TOKEN)
        utils.execute(
            "sed -i 's/^[ \\t]*limit_param_default[ \\t]*=.*$/limit_param_default = 2000/g' /etc/glance/glance-registry.conf")

    def _configureKeystone(self):
        if self.use_keystone:
            # Token
            self.TOKEN = self._generateToken()
            # Configure keystone
            utils.execute('ln -s /var/lib/keystone/keystone /var/lib/nova/keystone', check_exit_code=False)
            utils.execute('ln -s /var/lib/keystone/etc/keystone.conf /etc/keystone/keystone.conf',
                check_exit_code=False)
            utils.execute("sed -i 's@default_store = sqlite@default_store = mysql@g' /etc/keystone/keystone.conf")
            utils.execute(
                "sed -i 's@log_file = keystone.log@log_file = /var/log/keystone/keystone.log@g' /etc/keystone/keystone.conf")
            utils.execute(
                "sed -i 's,sqlite:///keystone.db,%s,g' /etc/keystone/keystone.conf" % self.keystone_sql_connection)
            utils.execute(
                "sed -i 's/admin_token = .*/admin_token = %s/g' %s" % (self.TOKEN, self.api_paste_config))
            utils.execute('cd /var/lib/keystone; python setup.py build')
            utils.execute('cd /var/lib/keystone; python setup.py install')

            cmd = '/var/lib/keystone/bin/keystone-manage -c /etc/keystone/keystone.conf'

            # Tenants
            utils.execute('%s tenant add admin' % cmd)
            if (len(self.default_username) > 0):
                self.default_tenant = ''
                utils.execute('%s tenant add %s' % (cmd, self.default_tenant))

            # Users
            utils.execute('%s user add admin %s' % (cmd, self.admin_password))
            if (len(self.default_username) > 0):
                utils.execute('%s user add %s %s' % (cmd, self.default_username, self.default_password))

            # Roles
            utils.execute('%s role add Admin' % cmd)
            utils.execute('%s role add Member' % cmd)
            utils.execute('%s role add KeystoneAdmin' % cmd)
            utils.execute('%s role add KeystoneServiceAdmin' % cmd)
            utils.execute('%s role add sysadmin' % cmd)
            utils.execute('%s role add netadmin' % cmd)
            utils.execute('%s role grant Admin admin admin' % cmd)
            if (len(self.default_username) > 0):
                utils.execute('%s role grant Member %s %s' % (cmd, self.default_username, self.default_tenant))
                utils.execute('%s role grant sysadmin %s %s' % (cmd, self.default_username, self.default_tenant))
                utils.execute('%s role grant netadmin %s %s' % (cmd, self.default_username, self.default_tenant))
                utils.execute('%s role grant Admin admin %s' % (cmd, self.default_tenant))
            utils.execute('%s role grant Admin admin' % cmd)
            utils.execute('%s role grant KeystoneAdmin admin' % cmd)
            utils.execute('%s role grant KeystoneServiceAdmin admin' % cmd)

            # Services
            utils.execute("%s service add nova compute 'Openstack Compute API service'" % cmd)
            utils.execute("%s service add glance image 'Openstack Image service'" % cmd)
            utils.execute("%s service add keystone identity 'Openstack Keystone service'" % cmd)

            #endpointTemplates
            utils.execute(
                "%s endpointTemplates add nova nova http://%s:%s/v1.1/%%tenant_id%% http://%s:8774/v1.1/%%tenant_id%%  http://%s:8774/v1.1/%%tenant_id%% 1 1" % (
                    cmd, self.osapi_hostname, self.osapi_port, self.ec2_dmz, self.ec2_dmz))
            utils.execute(
                "%s endpointTemplates add nova glance http://%s:9292/v1.1/%%tenant_id%% http://%s:9292/v1.1/%%tenant_id%% http://%s:9292/v1.1/%%tenant_id%% 1 1" % (
                    cmd, self.glance_hostname, self.ec2_dmz, self.ec2_dmz))
            utils.execute(
                "%s endpointTemplates add nova keystone http://%s:5000/v2.0 http://%s:35357/v2.0 http://%s:5000/v2.0 1 1" % (
                    cmd, self.osapi_hostname, self.ec2_dmz, self.ec2_dmz))

            utils.execute('%s token add %s admin admin 2015-02-05T00:00' % (cmd, self.TOKEN))

            # endpoint
            utils.execute("%s endpoint add admin 1" % cmd)
            utils.execute("%s endpoint add admin 2" % cmd)
            utils.execute("%s endpoint add admin 3" % cmd)
            if (len(self.default_username) > 0):
                utils.execute("%s endpoint add %s 1" % (cmd, self.default_tenant))
                utils.execute("%s endpoint add %s 2" % (cmd, self.default_tenant))
                utils.execute("%s endpoint add %s 3" % (cmd, self.default_tenant))

            # EC2 credentials
            utils.execute(
                "%s credentials add admin EC2 'admin' '%s' admin || echo 'no support for adding credentials'" % (
                    cmd, self.admin_password))
            if (len(self.default_username) > 0):
                utils.execute("%s credentials add %s EC2 '%s' '%s' %s || echo 'no support for adding credentials'" % (
                    cmd, self.default_username, self.default_username, self.default_password, self.default_tenant))

    def _configureHorizon(self):
        if self.use_horizon:
            self._configure_pip()
            utils.execute("easy_install /opt/pip_downloads/httplib2-0.6.0.tar.gz")
            utils.execute("easy_install /opt/pip_downloads/prettytable-0.5.tar.gz")
            utils.execute("easy_install /opt/pip_downloads/argparse-1.1.zip")
            utils.execute("easy_install /opt/pip_downloads/virtualenv-1.7.1.2.tar.gz")
            utils.execute('cd /var/lib/openstack.compute; python setup.py develop')
            utils.execute('cd /var/lib/openstackx; python setup.py develop')
            utils.execute('cd /var/lib/horizon/openstack-dashboard; python tools/install_venv.py')
            utils.execute('cd /var/lib/horizon/openstack-dashboard; tools/with_venv.sh dashboard/manage.py syncdb')
            shutil.copyfile(
                '/var/lib/stackops/django.wsgi',
                '/var/lib/horizon/openstack-dashboard/dashboard/wsgi/django.wsgi'
            )
            utils.execute('chown -R stackops:stackops /var/lib/horizon')

    def _configure_pip(self):
        if not os.path.exists('/root/.pip'):
            os.mkdir('/root/.pip')
        with open('/root/.pip/pip.conf', 'w') as f:
            f.write('''[global]
find-links = file:///opt/pip_downloads/
mirror = file:///opt/pip_downloads/
no_index = True''')

    def install(self, xmldoc, hostname):
        """
        Install all stuff needed to run a controller
        """
        result = ''
        try:
            if (getpass.getuser() == 'root'):
                # Install packages for component
                self.installPackages()
                self._configureMySQL()
                self._configureApache()
                self._configCerts()
                self._configureNovaManage()
                self._configureKeystone()
                self._configureGlance()
                self._configureHorizon()
                self._createNovaDatabase()
                if self.set_flavors:
                    self._deleteFlavors()
                self._addFlavors()
                #                self._createDefaultProjects()
                self._enableInitFiles()
                self._restartServices()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        if self.open_vm_tools:
            self._installDeb('open-vm-tools')
        self._installDeb('euca2ools')
        self._installDeb('cloud-utils')
        self._installDeb('glance')
        if self.install_mysql:
            utils.execute(
                'echo mysql-server-5.1 mysql-server/root_password password ' + self.mysql_root_password + ' | debconf-set-selections')
            utils.execute(
                'echo mysql-server-5.1 mysql-server/root_password_again password ' + self.mysql_root_password + ' | debconf-set-selections')
            utils.execute('echo mysql-server-5.1 mysql-server/start_on_boot boolean true')
            self._installDeb('mysql-server')
        if self.install_rabbitmq:
            self._installDeb('rabbitmq-server', False)
        self._installDeb('apache2')
        self._installDeb('libapache2-mod-wsgi')
        if self.use_keystone:
            self._installDeb('python-setuptools')
            self._installDeb('python-dev')
            self._installDeb('python-pastescript')
            self._installDeb('python-paste')
            self._installDeb('sqlite3')
            self._installDeb('python-pysqlite2')
            self._installDeb('python-webob')
            self._installDeb('libldap2-dev')
            self._installDeb('libsasl2-dev')
            self._installDeb('python-passlib')
        if self.use_horizon:
            self._installDeb('python-virtualenv')
            self._installDeb('python-pip')
        if self.glance_mount_type == 'nfs':
            self._installDeb('nfs-common')
        self._installDeb('python-numpy')


class ComputeConfig(Config):
    '''
    classdocs
    '''

    _filename = "nova-compute.conf"

    def __init__(self):
        '''
        Constructor
        '''
        self.PAGE_SIZE = 2 * 1024 * 1024
        self.BONUS_PAGES = 40

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
        self.nova_sql_connection = 'mysql://%s:%s@%s:%s/%s' % (
            self.nova_username, self.nova_password, self.nova_host, self.nova_port, self.nova_schema)

        # RabbitMQ
        self.rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')

        # NOVA-COMPUTE KVM specific
        self.libvirt_type = self._filler.getPropertyValue(xmldoc, 'libvirt', 'type')

        # ISCSI connectivity
        self.iscsi_ip_prefix = self._filler.getPropertyValue(xmldoc, 'iscsi', 'ip_prefix')
        self.num_targets = self._filler.getPropertyValue(xmldoc, 'iscsi', 'num_targets')
        self.storage_hostname = self._filler.getPropertyValue(xmldoc, 'iscsi', 'storage_hostname', 'nova-volume')

        # Network interfaces
        self.iface_list = self._operatingsystem.getNetworkConfiguration()
        self.management_interface = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_interface', 'eth0')
        for iface in self.iface_list:
            if iface['name'] == self.management_interface:
                self.my_ip = iface['address']

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
                'rw,dev,noexec,nosuid,auto,nouser,noatime,async,rsize=8192,wsize=8192')

        # NOVA-VOLUME QEMU Specific
        self.use_volume_nfs = self._filler.getPropertyValue(xmldoc, 'nas', 'use_nas', 'false') == 'true'
        if self.use_volume_nfs:
            self.volume_driver = self._filler.getPropertyValue(xmldoc, 'nas', 'volume_driver',
                'nova.volume.nas.QEMUDriver')
            self.volumes_path = self._filler.getPropertyValue(xmldoc, 'nas', 'volumes_path', '/var/lib/nova/volumes')
            self.volumes_mount_point = self._filler.getPropertyValue(xmldoc, 'nas', 'mount_point',
                '192.168.10.198:/volumes/vol1/openstack-nfs-volumes')
            self.volumes_mount_parameters = self._filler.getPropertyValue(xmldoc, 'nas', 'mount_parameters',
                'rw,dev,noexec,nosuid,auto,nouser,noatime,async,rsize=8192,wsize=8192')
        else:
            self.volume_driver = 'nova.volume.driver.ISCSIDriver'

        # Boot behaviour and virtio
        self.resume_guests_state_on_host_boot = self._filler.getPropertyValue(xmldoc, 'libvirt',
            'resume_guests_state_on_host_boot',
            'true')
        self.start_guests_on_host_boot = self._filler.getPropertyValue(xmldoc, 'libvirt', 'start_guests_on_host_boot',
            'false')
        self.libvirt_use_virtio_for_bridges = self._filler.getPropertyValue(xmldoc, 'libvirt',
            'libvirt_use_virtio_for_bridges', 'false')

        self.hugepages = self._filler.getPropertyValue(xmldoc, 'libvirt', 'hugepages', 'false') == 'true'
        self.hugepages_percentage = self._filler.getPropertyValue(xmldoc, 'libvirt', 'hugepages_percentage', '100')

        self.minimum_root_size = self._filler.getPropertyValue(xmldoc, 'libvirt', 'minimum_root_size', '1')

        # GLANCE Service configuration
        self.glance_hostname = self._filler.getPropertyValue(xmldoc, 'glance', 'hostname', 'localhost')
        self.glance_port = self._filler.getPropertyValue(xmldoc, 'glance', 'port', '9292')
        self.image_service = self._filler.getPropertyValue(xmldoc, 'glance', 'image_service',
            'nova.image.glance.GlanceImageService')
        # Bonding configurarion
        self.management_network_bond = self._filler.getPropertyValue(xmldoc, 'interfaces', 'management_network_bond')
        self.service_network_bond = self._filler.getPropertyValue(xmldoc, 'interfaces', 'service_network_bond')

        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'rabbit_host': self.rabbit_host,
                      'use_project_ca': self.use_project_ca,
                      'my_ip': self.my_ip,
                      # NOVA-COMPUTE SPECIFIC
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

        self._writeFile(self._filename, parameters)
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
        if self.instances_filesystem_mount_type == 'nfs':
            # configure NFS mount
            mpoint = '%s %s nfs %s 0 0' % (self.mount_point, self.instances_path, self.mount_parameters)
            utils.execute("sed -i 's#%s##g' /etc/fstab" % mpoint)
            utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
            # mount NFS remote
            utils.execute('mount -a')

    def _configureVolumeNFS(self):
        # configure NFS volumes mount
        if os.path.ismount(self.volumes_path):
            utils.execute('umount %s' % self.volumes_path)
        utils.execute("sed -i '\#%s#d' /etc/fstab" % self.volumes_path)
        mpoint = '%s %s nfs %s 0 0' % (self.volumes_mount_point, self.volumes_path, self.volumes_mount_parameters)
        utils.execute("sed -i 's#%s##g' /etc/fstab" % mpoint)
        utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
        # mount NFS remote
        utils.execute('mount -a')

    def _configureNovaVolumeHost(self):
        # add to /etc/hosts file the hostname of nova-volume
        if (self.storage_hostname != 'nova-controller'):
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
        utils.execute("sed -i '/hugepages/d' /var/lib/nova/nova/virt/libvirt.xml.template")
        utils.execute(
            "sed -i 's#</domain>#\\t<memoryBacking><hugepages/></memoryBacking>\\n</domain>#g' /var/lib/nova/nova/virt/libvirt.xml.template")

    def _disableSwap(self):
        utils.execute('sed -i /swap/d /etc/fstab')
        utils.execute('swapoff -a', check_exit_code=False)

    def _configureApparmor(self):
        utils.execute("sed -i '/hugepages/d' /etc/apparmor.d/abstractions/libvirt-qemu")
        utils.execute("echo '  owner /dev/hugepages/libvirt/qemu/* rw,' >> /etc/apparmor.d/abstractions/libvirt-qemu")

    def _configureLibvirt(self, hostname):
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
        utils.execute(
            '''sed -i 's/env libvirtd_opts="-d"/env libvirtd_opts="-d -l"/g' /etc/init/libvirt-bin.conf.disabled''',
            check_exit_code=False)
        utils.execute('''sed -i 's/env libvirtd_opts="-d"/env libvirtd_opts="-d -l"/g' /etc/init/libvirt-bin.conf''',
            check_exit_code=False)

    def _configureGlusterFS(self):
        if self.instances_filesystem_mount_type == 'glusterfs':
            # configure NFS mount
            utils.execute(
                'echo "\n %s %s glusterfs %s 0 0" >> /etc/fstab' % (
                    self.mount_point, self.instances_path, self.mount_parameters))
            # mount NFS remote
            utils.execute('mount -a')

    def _configureInitServices(self):
        # enable libvirt-bin
        utils.execute('mv /etc/init/libvirt-bin.conf.disabled /etc/init/libvirt-bin.conf', None, None, False)
        # enable controller components
        utils.execute('mv /etc/init/nova-compute.conf.disabled /etc/init/nova-compute.conf', None, None, False)

    def _restartServices(self):
        # start libvirt components
        utils.execute('stop libvirt-bin; start libvirt-bin')
        # start compute components
        utils.execute('stop nova-compute; start nova-compute')

    def install(self, xmldoc, hostname):
        result = ''
        try:
            if hostname != 'nova-controller':
                self._disableSwap()
            if self.hugepages and hostname != 'nova-controller':
                self._configureHugePages()
            self.installPackages() # Install packages for component

            self._configureFlatInterface(hostname) # Configure Flat Interface
            self._configureLinkAggregation() # NIC Bonding
            if self.hugepages and hostname != 'nova-controller':
                self._configureApparmor()
            if self.use_volume_nfs:
                self._configureVolumeNFS() # Configure Volume NFS
            self._configureNFS() # Configure NFS
            self._configureGlusterFS() # Configure GlusterFS
            self._configureNovaVolumeHost() # Configure NovaVolume host name
            self._configureLibvirt(hostname) # Enable Libvirt communication
            self._configureInitServices()
            self._restartServices()
        except  Exception as inst:
            log.err()
            result = 'ERROR: %s' % str(inst)
        return result

    def _configureLinkAggregation(self):
        """Configure initial network link aggregation (NIC bonding)"""

        # Test if management network interdfce is dhcp configured.
        interfaces_content = open('/etc/network/interfaces').read()
        if not re.search(r'^iface[ \t]+(eth|bond)0[ \t]+inet[ \t]+dhcp', interfaces_content, re.I | re.M):
            return

        # Write new configuration.
        interfaces_content = templates['interfaces']
        if self.management_network_bond:
            interfaces_content += templates['iface_bonding'] % {'iface': self.management_network_bond, 'bond': 'bond0'}
        if self.service_network_bond:
            interfaces_content += templates['iface_bonding'] % {'iface': self.service_network_bond, 'bond': 'bond1'}
        with open('/etc/network/interfaces', 'w') as f:
            f.write(interfaces_content)
        if os.path.exists('/etc/modprobe.d/aliases.conf'):
            aliases_content = []
            for line in open('/etc/modprobe.d/aliases.conf'):
                if not 'bonding' in line:
                    aliases_content.append(line)
            aliases_content = ''.join(aliases_content)
        else:
            aliases_content = ''
        aliases_content += 'alias bond0 bonding\nalias bond1 bonding\noptions bonding mode=1 miimon=100 max_bonds=2'
        with open('/etc/modprobe.d/aliases.conf', 'w') as f:
            f.write(aliases_content)

        # Manual setup without system reboot.
        eth0_conf = utils.get_ip_info('eth0')
        if eth0_conf:
            eth0_conf = eth0_conf[0]
            utils.execute('modprobe bonding')
            utils.execute('ifconfig bond0 %s netmask %s' % eth0_conf[2:])
            utils.execute('ifenslave bond0 eth0')
            utils.execute('ifconfig eth1 up')
            utils.execute('ifconfig bond1 up')
            utils.execute('ifenslave bond1 eth1')
            if self.management_network_bond:
                utils.execute('ifenslave bond0 ' + self.management_network_bond)
            if self.service_network_bond:
                utils.execute('ifenslave bond1 ' + self.service_network_bond)

        # Wait for bonding up.
        time.sleep(10)

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('nfs-common')
        self._installDeb('kvm')
        self._installDeb('kvm-pxe')
        self._installDeb('iptables')
        self._installDeb('ebtables')
        self._installDeb('user-mode-linux')
        self._installDeb('libvirt-bin')
        self._installDeb('python-libvirt')
        self._installDeb('ifenslave')


class NetworkConfig(Config):
    '''
    classdocs
    '''

    _filename = "nova-network.conf"

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

        # EC2 API
        self.ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        self.ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')
        # NOVA-NETWORK SPECIFIC
        self.dhcpbridge = self._filler.getPropertyValue(xmldoc, 'dhcpbridge', 'process')
        self.dhcpbridge_flagfile = self._filler.getPropertyValue(xmldoc, 'dhcpbridge', 'file')
        self.routing_source_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'routing_source_ip', None)
        self.floating_range = self._filler.getPropertyValue(xmldoc, 'interfaces', 'floating_range', None)

        # Default Fixed range configuration
        self.network_manager = self._filler.getPropertyValue(xmldoc, 'network', 'type',
            'nova.network.manager.FlatDHCPManager')
        self.fixed_range = self._filler.getPropertyValue(xmldoc, 'network', 'fixed_range', '10.0.0.0/8')
        self.network_size = self._filler.getPropertyValue(xmldoc, 'network', 'network_size', '256')
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
            if (self.routing_source_ip == None):
                if iface['name'] == self.public_interface:
                    self.routing_source_ip = iface['address']

        self.public_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip', '')
        self.public_ip_mask = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip_mask', '255.255.255.255')
        self.public_ip_gateway = self._filler.getPropertyValue(xmldoc, 'interfaces', 'public_ip_gateway', '')
        self.firewall_public_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'firewall_public_ip',
            'false') == 'true'

        octets = self.fixed_range.split('/')[0].split('.')
        self.flat_network_dhcp_start = '%s.%s.%s.%i' % (octets[0], octets[1], octets[2], int(octets[3]) + 2)

        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'rabbit_host': self.rabbit_host,
                      'use_project_ca': self.use_project_ca,
                      'my_ip': self.my_ip,
                      # NOVA-NETWORK SPECIFIC
                      'dhcpbridge': self.dhcpbridge,
                      'dhcpbridge_flagfile': self.dhcpbridge_flagfile,
                      'routing_source_ip': self.routing_source_ip,
                      'public_interface': self.public_interface,
                      'network_manager': self.network_manager,
                      'flat_network_dhcp_start': self.flat_network_dhcp_start,
                      'fixed_range': self.fixed_range,
                      'ec2_host': self.ec2_hostname,
                      'ec2_dmz_host': self.ec2_dmz,
                      'override_bridge_interface': self.flat_interface}

        self._writeFile(self._filename, parameters)
        return

    def _addFloatingIP(self, ip_list):
        # Add floating ips
        if ip_list.startswith('['):
            ips = eval(ip_list)
            for ip in ips:
                utils.execute('/var/lib/stackops/addfloatingip.sh %s %s %s %s %s' % (
                self.nova_host, self.nova_port, self.nova_username, self.nova_password, ip))
        else:
            utils.execute('/var/lib/nova/bin/nova-manage float create %s' % ip_list)

    def _addFirewallRules(self, publicip, bridgeif):
        shutil.copyfile('/var/lib/stackops/rules.iptables', '/etc/iptables/rules.v4')
        utils.execute("sed -i 's/127.0.0.1/%s/g' /etc/iptables/rules.v4" % publicip)
        utils.execute("sed -i 's/BRIDGEIF/%s/g' /etc/iptables/rules.v4" % bridgeif)
        utils.execute("service iptables-persistent stop; service iptables-persistent start", check_exit_code=False)

    def install(self, xmldoc, hostname):
        result = ''
        try:
            # Install packages for component
            self.installPackages()

            if (hostname == 'nova-controller'):
                utils.execute('echo "dummy" >> /etc/modules')
                utils.execute('modprobe dummy')
                utils.execute('ifconfig dummy0 0.0.0.0')

            # nova.conf in bin linked to network info
            utils.execute('rm /var/lib/nova/bin/nova.conf', None, None, False)
            utils.execute('ln -s /etc/nova/nova-network.conf /var/lib/nova/bin/nova.conf')

            # Remove old configurations, if any
            utils.execute("sed -i '{:q;N;s/\\tpost-up[^][^]*.\\n//g;t q}' /etc/network/interfaces")
            for networkType in ['static', 'dhcp']:
                # enable flat interface
                utils.execute(
                    "sed -i 's/inet %s/inet %s\\n\\tpost-up ifconfig %s 0.0.0.0/g' /etc/network/interfaces" % (
                        networkType, networkType, self.flat_interface))
                # Configure Public interface
                if (self.public_ip_mask != '255.255.255.255'):
                    utils.execute(
                        "sed -i 's/inet %s/inet %s\\n\\tpost-up ifconfig %s %s netmask %s\\n\\tpost-up route add default gw %s %s/g' /etc/network/interfaces" % (
                            networkType, networkType, self.public_interface, self.public_ip, self.public_ip_mask,
                            self.public_ip_gateway, self.public_interface))

            utils.execute('ifconfig ' + self.flat_interface + ' 0.0.0.0')
            # Configure Public interface
            if (self.public_ip_mask != '255.255.255.255'):
                utils.execute(
                    'ifconfig %s %s netmask %s' % (self.public_interface, self.public_ip, self.public_ip_mask))
                utils.execute('route del default', check_exit_code=False)
                utils.execute('route add default gw %s %s' % (self.public_ip_gateway, self.public_interface))

            # create a small network
            bridgeif = 'br100'
            if self.network_manager == 'nova.network.manager.VlanManager':
                utils.execute(
                    '/var/lib/nova/bin/nova-manage network create service %s 1 %s --vlan=%s --bridge_interface=%s --dns1=%s --dns2=%s' % (
                        self.fixed_range, self.network_size, self.vlanstart, self.bridged_interface, self.dns1,
                        self.dns2))
                bridgeif = 'br%s' % self.vlanstart
            else:
                utils.execute(
                    '/var/lib/nova/bin/nova-manage network create service %s 1 %s --bridge=%s --bridge_interface=%s --dns1=%s --dns2=%s' % (
                        self.fixed_range, self.network_size, self.bridge, self.bridged_interface, self.dns1, self.dns2))
                # floating network
            self._addFloatingIP(self.floating_range)

            # add firewall to public ip if necessary
            if self.firewall_public_ip and len(self.public_ip) > 0:
                self._addFirewallRules(self.public_ip, bridgeif)

            # enable ipforwarding
            utils.execute("sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf")
            utils.execute("sysctl -p /etc/sysctl.conf")

            # enable network components
            utils.execute('mv /etc/init/nova-network.conf.disabled /etc/init/nova-network.conf', None, None, False)
            # start network components
            utils.execute('stop nova-network; start nova-network')
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('bridge-utils')
        self._installDeb('dnsmasq-base')
        self._installDeb('iptables')
        self._installDeb('iptables-persistent', interactive=False)
        self._installDeb('ebtables')


class VolumeConfig(Config):
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

        # NOVA-VOLUME specific
        self.use_local_volumes = self._filler.getPropertyValue(xmldoc, 'iscsi', 'use_local_volumes')

        # LVM device to use as block storage
        self.lvm_device = self._filler.getPropertyValue(xmldoc, 'iscsi', 'lvm_device', None)

        parameters = {'lock_path': self.lock_path,
                      'verbose': self.verbose,
                      'nodaemon': self.nodaemon,
                      'sql_connection': self.nova_sql_connection,
                      'auth_driver': self.auth_driver,
                      'logdir': self.logdir,
                      'state_path': self.state_path,
                      'rabbit_host': self.rabbit_host,
                      'use_project_ca': self.use_project_ca,
                      'my_ip': self.my_ip,
                      # NOVA-VOLUME specific
                      'use_local_volumes': self.use_local_volumes
        }

        self._writeFile(self._filename, parameters)
        return

    def install(self, xmldoc, hostname):
        result = ''
        try:
            # Install packages for component
            self.installPackages()

            # enable controller components
            utils.execute('mv /etc/init/nova-volume.conf.disabled /etc/init/nova-volume.conf', None, None, False)
            # enable iscsi target
            utils.execute("sed -i 's/false/true/g' /etc/default/iscsitarget")
            utils.execute('service iscsitarget start')
            # create nova-volumes
            utils.execute('vgremove -ff nova-volumes; pvcreate -ffy ' + self.lvm_device)
            utils.execute('vgcreate nova-volumes ' + self.lvm_device)
            # start compute components
            utils.execute('stop nova-volume; start nova-volume')
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('kpartx')
        self._installDeb('lvm2')
        self._installDeb('iscsitarget')


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
                      'my_ip': self.my_ip,
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

    def install(self, xmldoc, hostname):
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
                      'rabbit_host': self.rabbit_host,
                      'use_project_ca': self.use_project_ca,
                      'my_ip': self.my_ip,
                      'volume_driver': self.volume_driver,
                      'volumes_path': self.volumes_path,
                      'host': self.nova_volume_host}

        self._writeFile(self._filename, parameters)
        return

    def _enableInitFiles(self):
        utils.execute('mv /etc/init/nova-volume.conf.disabled /etc/init/nova-volume.conf', None, None, False)

    def _restartServices(self):
        utils.execute('stop nova-volume; start nova-volume')

    def _configureNFS(self):
        # configure NFS mount
        if os.path.ismount(self.volumes_path):
            utils.execute('umount %s' % self.volumes_path)
        utils.execute("sed -i '\#%s#d' /etc/fstab" % self.volumes_path)
        mpoint = '%s %s nfs %s 0 0' % (self.mount_point, self.volumes_path, self.mount_parameters)
        utils.execute("sed -i 's#%s##g' /etc/fstab" % mpoint)
        utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
        # mount NFS remote
        utils.execute('mount -a')

    def install(self, xmldoc, hostname):
        result = ''
        try:
            # Install packages for component
            self.installPackages()
            # Mount shared file system
            self._configureNFS()
            # enable controller components
            self._enableInitFiles()
            # start compute components
            self._restartServices()
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('qemu-kvm')
        self._installDeb('nfs-common')


class Configurator(object):
    '''
    classdocs
    '''

    _controllerConfig = ControllerConfig()
    _computeConfig = ComputeConfig()
    _networkConfig = NetworkConfig()
    _volumeConfig = VolumeConfig()
    _nexentaVolumeConfig = NexentaVolumeConfig()
    _qemuVolumeConfig = QEMUVolumeConfig()
    _filler = install.Filler();

    def __init__(self):
        '''
        Constructor
        '''

    def _removeRepos(self):
        utils.execute('sed -i /precise-updates/d /etc/apt/sources.list')
        utils.execute('sed -i /precise-security/d /etc/apt/sources.list')
        utils.execute('sed -i /archive.ubuntu.com/d /etc/apt/sources.list')
        utils.execute('rm /etc/apt/sources.list.d/stackops.list || true')
        utils.execute('apt-get -y update')

    def _installDeb(self, name, interactive=True):
        if (interactive):
            utils.execute('apt-get -y install %s' % name)
        else:
            utils.execute('DEBIAN_FRONTEND=noninteractive apt-get -y install %s' % name)

    def _changeHostname(self, hostname):
        # Change first the hostname
        utils.execute('hostname ' + hostname)
        utils.execute('echo "' + hostname + '" > /etc/hostname')
        utils.execute("sed -i 's/stackops-node/" + hostname + "/g' /etc/hosts")

    def _configureNTPClient(self, ntpHost):
        # Change default ntp server to client choice
        utils.execute("sed -i 's/server ntp.ubuntu.com/server " + ntpHost + "/g' /etc/ntp.conf")
        utils.execute("service ntp stop; ntpdate -u %s; service ntp start" % ntpHost, check_exit_code=False)

    def _createCollectdConfigFile(self, configType, controllerIP):
        path = '/etc/collectd'
        filename = 'collectd.conf'
        try:
            if not os.path.exists(path):
                raise Exception("Directory " + path + " does not exists")
        except Exception:
            raise Exception("Error reading directory " + path)
        try:
            f = open(path + '/' + filename, 'w')
            f.write('# This is an automatically generated file by stackops\n')
            f.write('# Change the parameters manually at your own risk\n')
            f.write('FQDNLookup true\n')
            f.write('\n')
            f.write('LoadPlugin "logfile"\n')
            f.write('LoadPlugin "network"\n')
            f.write('\n')
            if configType & 1 == 1:
                f.write('# Server configuration\n')
                f.write('LoadPlugin "rrdtool"\n')
                f.write('\n')

            f.write('# Client configuration\n')
            f.write('LoadPlugin "interface"\n')
            f.write('LoadPlugin "cpu"\n')
            f.write('LoadPlugin "memory"\n')
            f.write('LoadPlugin "df"\n')
            f.write('LoadPlugin "disk"\n')
            f.write('LoadPlugin "vmem"\n')
            f.write('LoadPlugin "swap"\n')
            if (configType & 8 == 8):
                f.write('# compute node specific\n')
                f.write('LoadPlugin "libvirt"\n')
            if (configType & 2 == 2):
                f.write('# network node specific\n')
                f.write('LoadPlugin "iptables"\n')

            f.write('\n')
            f.write('<Plugin "network">\n')
            if configType & 1 == 1:
                f.write('  Listen "' + controllerIP + '"\n')
            f.write('  Server "' + controllerIP + '"\n')
            f.write('</Plugin>\n')
            f.write('\n')

            if configType & 1 == 1:
                f.write('<Plugin rrdtool>\n')
                f.write('  DataDir "/var/lib/collectd/rrd"\n')
                f.write('</Plugin>\n')
                f.write('\n')

            f.write('<Plugin "interface">\n')
            f.write('  Interface "lo"\n')
            f.write('  IgnoreSelected true\n')
            f.write('</Plugin>\n')

            if (configType == 8) or (configType == 15):
                f.write('<Plugin "libvirt">\n')
                f.write('  Connection "qemu:///system"\n')
                f.write('  HostnameFormat "name"\n')
                f.write('</Plugin>\n')

            f.close()
        except Exception:
            print "Error writing file. " + path + '/' + filename
            raise Exception("Error writing file. " + path + '/' + filename)


    def _configureXymonServer(self, xymon_ip):
        # Change default ntp server to client choice
        self._installDeb('xymon-client', interactive=False)
        utils.execute("sed -i 's/127.0.0.1/%s/g' /etc/default/hobbit-client" % xymon_ip)
        utils.execute("sed -i 's/.stackops.org//g' /etc/default/hobbit-client")
        utils.execute(
            "sed -i 's/grep -v tmpfs | awk/grep -v tmpfs | grep -v nfs | awk/g' /usr/lib/hobbit/client/bin/hobbitclient-linux.sh")
        utils.execute(
            "sed -i 's/df -Pl -x iso9660/df -P -x iso9660/g' /usr/lib/hobbit/client/bin/hobbitclient-linux.sh")
        utils.execute("service hobbit-client stop; service hobbit-client start", check_exit_code=False)

    def _blacklistFb(self):
        # Blacklist framebuffer
        utils.execute('sed -i /vga16fb/d /etc/modprobe.d/blacklist-framebuffer.conf ')
        utils.execute('echo "blacklist vga16fb" >> /etc/modprobe.d/blacklist-framebuffer.conf ')

    def _publishKeys(self, authorized_keys, root_pass="", stackops_pass=""):
        # Publish keys and do not allow ssh user and pass
        if len(authorized_keys) > 0:
            utils.execute("su stackops -c 'rm -fR ~/.ssh'", check_exit_code=False)
            utils.execute("su stackops -c 'mkdir ~/.ssh'", check_exit_code=False)
            utils.execute("su stackops -c 'chmod 700 ~/.ssh'")
            authorized_keys = authorized_keys.replace(',', '\n')
            utils.execute("su stackops -c 'echo \"%s\" > /home/stackops/.ssh/authorized_keys'" % authorized_keys)
            utils.execute("su stackops -c 'chmod 600 ~/.ssh/authorized_keys'")
            utils.execute("sed -i 's/PermitRootLogin yes/PermitRootLogin no/g' /etc/ssh/sshd_config ")
            utils.execute("sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/g' /etc/ssh/sshd_config ")
            utils.execute("sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config ")
            utils.execute("sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config ")
            utils.execute("sed -i 's/%sudo ALL=(ALL) ALL/%sudo ALL=(ALL) NOPASSWD:ALL/g' /etc/sudoers")
            with open('/etc/ssh/sshd_config', 'a') as ssh_config:
                ssh_config.write('\nUseDNS no')
            utils.execute("adduser stackops sudo")
            utils.execute("service ssh restart")
        if len(root_pass) > 0:
            utils.execute("echo 'root:%s'|chpasswd" % root_pass)
        if len(stackops_pass) > 0:
            utils.execute("echo 'stackops:%s'|chpasswd" % stackops_pass)

    def detectConfiguration(self):
        cloud = None
        node = self._filler.createNode(cloud)
        return node

    def importConfiguration(self, xml):
        """
        Import the configuration from the XML definition file, and configure the selected nodes.
        You must be root to execute this method
        """
        if getpass.getuser() == 'root':
            self._blacklistFb()
            self._removeRepos()
            # Change hostname from XML information
            hostname = xml.get_software().get_os().get_network().get_hostname()
            # Change hostname
            self._changeHostname(hostname)
            configType = 0
            ntpServer = None
            xymon_server = None
            collectd_listener = None
            authorized_keys = None
            for component in xml.get_cloud().get_component():
                if authorized_keys is None: # Only once...
                    authorized_keys = self._filler.getPropertyValue(component, 'hardening', 'authorized_keys', '')
                    root_pass = self._filler.getPropertyValue(component, 'hardening', 'root_password', '')
                    stackops_pass = self._filler.getPropertyValue(component, 'hardening', 'stackops_password', '')
                    self._publishKeys(authorized_keys, root_pass, stackops_pass)
                if ntpServer == None: # Only once...
                    ntpServer = self._filler.getPropertyValue(component, 'infrastructure', 'ntp_server',
                        'ntp.ubuntu.com')
                    self._configureNTPClient(ntpServer)
                if xymon_server == None: # Only once...
                    xymon_server = self._filler.getPropertyValue(component, 'monitoring', 'xymon_server', '')
                    if len(xymon_server) > 0:
                        self._configureXymonServer(xymon_server)
                if collectd_listener == None: # Only once...
                    collectd_listener = self._filler.getPropertyValue(component, 'monitoring', 'collectd_listener',
                        'localhost')
                    # Is a Controller?
                if component.get_name() == 'controller':
                    configType |= 1
                    self._controllerConfig.write(component)
                    result = self._controllerConfig.install(component, hostname)
                    if len(result) > 0:
                        return result
                    use_nexenta = self._filler.getPropertyValue(component, 'nexenta_san', 'use_nexenta',
                        'false') == 'true'
                    if use_nexenta:
                        self._nexentaVolumeConfig.write(component)
                        result = self._nexentaVolumeConfig.install(component, hostname)
                        if len(result) > 0:
                            return result
                    use_nfs = self._filler.getPropertyValue(component, 'nas', 'use_nas',
                        'false') == 'true'
                    if use_nfs:
                        self._qemuVolumeConfig.write(component)
                        result = self._qemuVolumeConfig.install(component, hostname)
                        if len(result) > 0:
                            return result
                            # Is a Compute?
                if component.get_name() == 'compute':
                    configType |= 8
                    self._computeConfig.write(component)
                    result = self._computeConfig.install(component, hostname)
                    if len(result) > 0:
                        return result
                        # Is a Network?
                if component.get_name() == 'network':
                    configType |= 2
                    self._networkConfig.write(component)
                    result = self._networkConfig.install(component, hostname)
                    if len(result) > 0:
                        return result
                        # Is a Volume?
                if component.get_name() == 'volume':
                    use_nexenta = self._filler.getPropertyValue(component, 'nexenta_san', 'use_nexenta',
                        'false') == 'true'
                    use_nfs = self._filler.getPropertyValue(component, 'nas', 'use_nas',
                        'false') == 'true'
                    if not use_nexenta and not use_nfs:
                        configType |= 4
                        self._volumeConfig.write(component)
                        result = self._volumeConfig.install(component, hostname)
                        if len(result) > 0:
                            return result
                            # Add the rest of the components here...
                            #
                            #
                            #
                            # configType = 15, single node
                            # configType = 7, dual node controller
                            # configType = 1, 2, 4 multinode
                            # configType = 8 dual o multinode (compute node)

                        # Deprecated.
                        #                    self._createCollectdConfigFile(configType,collectd_listener)
                        #                    utils.execute('service collectd restart')
            return ''
        else:
            return 'You should run this program as super user.'

# This is a test
# Templates for simple config-files generation.
templates = {

    'interfaces': """
auto eth0
allow-bond0 eth0
iface eth0 inet manual
    bond-master bond0

auto eth1
allow-bond1 eth1
iface eth1 inet manual
    bond-master bond1

auto bond0
iface bond0 inet dhcp
        bond-mode 1
        miimon 100

auto bond1
iface bond1 inet manual
    bond-mode 1
    miimon 100
    post-up ifconfig $IFACE up
    pre-down ifconfig $IFACE down
    """,

    'iface_bonding': """
auto %(iface)s
allow-%(bond)s %(iface)s
iface %(iface)s inet manual
    bond-master %(bond)s
    """,

    }

