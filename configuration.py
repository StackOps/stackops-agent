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
        if interactive:
            utils.execute('apt-get -y install %s' % name)
        else:
            utils.execute('DEBIAN_FRONTEND=noninteractive apt-get -y install %s' % name)

    def installPackages(self):
        raise NotImplementedError("Should have implemented this")


    def whatIsMyIp(self, management_interface):
        iface_list = self._operatingsystem.getNetworkConfiguration()
        myip = '127.0.0.1'
        for iface in iface_list:
            if iface['name'] == management_interface:
                myip = iface['address']
        return myip


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
        shutil.rmtree('/var/lib/rabbitmq', ignore_errors=True)
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
        self.ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname', '127.0.0.1')
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

        utils.execute('sed -i /catalog.RegionOne.identity.publicURL/d /etc/keystone/default_catalog.templates')
        utils.execute('sed -i /catalog.RegionOne.compute.publicURL/d /etc/keystone/default_catalog.templates')
        utils.execute('sed -i /catalog.RegionOne.volume.publicURL/d /etc/keystone/default_catalog.templates')
        utils.execute('sed -i /catalog.RegionOne.ec2.publicURL/d /etc/keystone/default_catalog.templates')
        utils.execute('sed -i /catalog.RegionOne.image.publicURL/d /etc/keystone/default_catalog.templates')

        public_ip = self.ec2_hostname
        public_port = '80'

        utils.execute(
            'echo "catalog.RegionOne.identity.publicURL = http://%s:%s/keystone/v2.0" >> /etc/keystone/default_catalog.templates' % (
            public_ip, public_port))
        utils.execute(
            'echo "catalog.RegionOne.compute.publicURL = http://%s:%s/compute/v1.1/\$(tenant_id)s" >> /etc/keystone/default_catalog.templates' % (
                public_ip, public_port))
        utils.execute(
            'echo "catalog.RegionOne.volume.publicURL = http://%s:%s/volume/v1/\$(tenant_id)s" >> /etc/keystone/default_catalog.templates' % (
                public_ip, public_port))
        utils.execute(
            'echo "catalog.RegionOne.ec2.publicURL = http://%s:%s/services/Cloud" >> /etc/keystone/default_catalog.templates' % (
                public_ip, public_port))
        utils.execute(
            'echo "catalog.RegionOne.image.publicURL = http://%s:%s/glance/v1" >> /etc/keystone/default_catalog.templates' % (
                public_ip, public_port))

        utils.execute("service keystone restart")
        utils.execute("keystone-manage db_sync")
        # Configure service users/roles
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s tenant-create --name=admin' % (self.endpoint, self.admin_password))
        admin_tenant = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s tenant-create --name=service' % (self.endpoint, self.admin_password))
        service_tenant = self.get_id(stdout)
        # StackOps Portal default tenant
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s tenant-create --name=portal' % (self.endpoint, self.admin_password))
        portal_tenant = self.get_id(stdout)

        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-create --name=admin --pass=%s --email=admin@domain.com' % (
                self.endpoint, self.admin_password, self.admin_password))
        admin_user = self.get_id(stdout)
        # Stackops Portal default user
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-create --name=portal --pass=%s --tenant_id %s --email=portal@domain.com' % (
                self.endpoint, self.admin_password, self.admin_password, portal_tenant))
        portal_user = self.get_id(stdout)
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
            'keystone --endpoint %s --token %s role-create --name=KeystoneServiceAdmin' % (
                self.endpoint, self.admin_password))
        keystone_service_admin_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=Member' % (self.endpoint, self.admin_password))
        member_role = self.get_id(stdout)
        # StackOps Portal role
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=ROLE_PORTAL_ADMIN' % (
                self.endpoint, self.admin_password))
        portal_admin_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s role-create --name=ROLE_PORTAL_USER' % (
                self.endpoint, self.admin_password))
        portal_user_role = self.get_id(stdout)
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
                self.endpoint, self.admin_password, admin_user, admin_role, admin_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
                self.endpoint, self.admin_password, admin_user, keystone_admin_role, admin_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
                self.endpoint, self.admin_password, admin_user, keystone_service_admin_role, admin_tenant))
        # StackOps Portal user-role-add
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
                self.endpoint, self.admin_password, portal_user, portal_admin_role, portal_tenant))
        (stdout, stderr) = utils.execute(
            'keystone --endpoint %s --token %s user-role-add --user %s --role %s --tenant_id %s' % (
                self.endpoint, self.admin_password, portal_user, portal_user_role, portal_tenant))
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
        shutil.rmtree('/var/lib/keystone', ignore_errors=True)
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

        # images store type
        self.glance_mount_type = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_type', 'local')
        if self.glance_mount_type == 'local':
            self.glance_mount_point = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_point', None)
            self.glance_mount_parameters = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_parameters', None)
        else:
            self.glance_mount_point = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_point',
                '192.168.10.198:/volumes/vol1/openstack-nfs-images')
            self.glance_mount_parameters = self._filler.getPropertyValue(xmldoc, 'glance', 'mount_parameters',
                'rw,dev,noexec,nosuid,auto,nouser,noatime,async,rsize=8192,wsize=8192')

        return

    def _configureGlance(self):
        utils.execute(
            "sed -i 's/%%SERVICE_PASSWORD%%/%s/g' /etc/glance/glance-api-paste.ini" % self.admin_password)
        utils.execute(
            "sed -i 's/%%SERVICE_PASSWORD%%/%s/g' /etc/glance/glance-registry-paste.ini" % self.admin_password)
        utils.execute(
            "sed -i 's/%%SERVICE_TENANT_NAME%%/%s/g' /etc/glance/glance-api-paste.ini" % 'admin')
        utils.execute(
            "sed -i 's/%%SERVICE_TENANT_NAME%%/%s/g' /etc/glance/glance-registry-paste.ini" % 'admin')
        utils.execute(
            "sed -i 's/%%SERVICE_USER%%/%s/g' /etc/glance/glance-api-paste.ini" % 'admin')
        utils.execute(
            "sed -i 's/%%SERVICE_USER%%/%s/g' /etc/glance/glance-registry-paste.ini" % 'admin')
        utils.execute(
            "sed -i 's#sql_connection = sqlite:////var/lib/glance/glance.sqlite#sql_connection = %s#g' /etc/glance/glance-registry.conf" % self.glance_sql_connection)
        utils.execute('sed -i "/paste_deploy/d" /etc/glance/glance-registry.conf')
        utils.execute('echo "[paste_deploy]" >> /etc/glance/glance-registry.conf')
        utils.execute('sed -i "/flavor = keystone/d" /etc/glance/glance-registry.conf')
        utils.execute('echo "flavor = keystone" >> /etc/glance/glance-registry.conf')
        utils.execute('sed -i "/paste_deploy/d" /etc/glance/glance-api.conf')
        utils.execute('echo "[paste_deploy]" >> /etc/glance/glance-api.conf')
        utils.execute('sed -i "/flavor = keystone/d" /etc/glance/glance-api.conf')
        utils.execute('echo "flavor = keystone" >> /etc/glance/glance-api.conf')

        utils.execute("service glance-api stop && service glance-registry stop")

        utils.execute('rm -fr /var/lib/glance/images', check_exit_code=False)
        utils.execute('mkdir -p /var/lib/glance/images', check_exit_code=False)
        utils.execute('chown glance:glance -R /var/lib/glance/images')
        if self.glance_mount_type == 'nfs':
            # configure NFS mount
            mpoint = '%s %s nfs %s 0 0' % (
                self.glance_mount_point, '/var/lib/glance/images', self.glance_mount_parameters)
            utils.execute("sed -i 's#%s##g' /etc/fstab" % mpoint)
            utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
            # mount NFS remote
            utils.execute('mount -a')

        utils.execute("service glance-api start && service glance-registry start")

        utils.execute("glance-manage version_control 0")
        utils.execute("glance-manage db_sync")
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
        utils.execute(
            "apt-get -y --purge remove glance glance-api glance-client glance-common glance-registry python-mysqldb nfs-common"
            ,
            check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        shutil.rmtree('/var/lib/glance', ignore_errors=True)
        return

    def installPackages(self):
        self.installPackagesCommon()
        if self.glance_mount_type == 'nfs':
            self._installDeb('nfs-common')
        self._installDeb('glance glance-api glance-client glance-common glance-registry python-mysqldb')
        return


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
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init/nova-api.conf" % '--flagfile=/etc/nova/nova-api-stackops.conf')
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
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init/nova-scheduler.conf" % '--flagfile=/etc/nova/nova-scheduler-stackops.conf')
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
                      'override_bridge_interface': self.flat_interface}

        self._writeFile(self._filename, parameters)
        utils.execute("service nova-network stop", check_exit_code=False)
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init/nova-network.conf" % '--flagfile=/etc/nova/nova-network-stackops.conf')
        if os.path.exists(self.state_path):
            utils.execute('chown nova:nova -R %s' % self.state_path)
        utils.execute("service nova-network start")
        return

    def _addFloatingIP(self, ip_list):
        # Add floating ips
        if ip_list.startswith('['):
            ips = eval(ip_list)
            for ip in ips:
                utils.execute('/var/lib/stackops/addfloatingip.sh %s %s %s %s %s' % (
                    self.nova_host, self.nova_port, self.nova_username, self.nova_password, ip))
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
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init/nova-compute.conf" % '--flagfile=/etc/nova/nova-compute-stackops.conf')
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova-compute.conf#%s#g' /etc/init/nova-compute.conf" % ' ')
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
                if self.storage_hostname != 'nova-controller':
                    self._configureNovaVolumeHost() # Configure NovaVolume host name
                if self.use_iscsi:
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
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init/nova-consoleauth.conf" % '--flagfile=/etc/nova/nova-vncproxy-stackops.conf')
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
        utils.execute(
            "sed -i 's#--flagfile=/etc/nova/nova.conf#%s#g' /etc/init/nova-volume.conf" % '--flagfile=/etc/nova/nova-volume-stackops.conf')
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
                      'notification_driver': 'nova.notifier.rabbit_notifier',
                      'notification_topics': 'notifications,monitor',
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

    def install(self, hostname):
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

        # JVM configuration
        utils.execute('sed -i /JAVA_OPTS/d /etc/default/tomcat7')
        utils.execute('''echo 'JAVA_OPTS="-Djava.awt.headless=true -Xmx768m -XX:+UseConcMarkSweepGC"' >> /etc/default/tomcat7''')

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
        self._installDeb('openjdk-7-jdk tomcat7', interactive=False)
        return

class OSConfigurator(object):
    '''
    classdocs
    '''

    _mysqlMasterConfig = MySQLMasterConfig()
    _rabbitMasterConfig = RabbitMQMasterConfig()
    _keystoneConfig = KeystoneConfig()
    _glanceConfig = GlanceConfig()
    _novaApiConfig = NovaApiConfig()
    _novaSchedulerConfig = NovaSchedulerConfig()
    _novaVncProxyConfig = NovaVncProxyConfig()
    _novaNetworkConfig = NovaNetworkConfig()
    _novaComputeConfig = NovaComputeConfig()
    _horizonConfig = HorizonConfig()
    _novaVolumeLinuxLVMConfig = NovaVolumeLinuxLVMConfig()
    _nexentaVolumeConfig = NexentaVolumeConfig()
    _qemuVolumeConfig = QEMUVolumeConfig()
    _portalConfig = PortalConfig()
    _filler = install.Filler();

    def __init__(self):
        '''
        Constructor
        '''

    def _configureLinkAggregation(self, management_network_bond=None, service_network_bond=None):
        """Configure initial network link aggregation (NIC bonding)"""

        self._installDeb("ifenslave", interactive=False)

        # Test if management network interdfce is dhcp configured.
        interfaces_content = open('/etc/network/interfaces').read()
        if not re.search(r'^iface[ \t]+(eth|bond)0[ \t]+inet[ \t]+dhcp', interfaces_content, re.I | re.M):
            return

        # Write new configuration.
        interfaces_content = templates['interfaces']
        aliases_content_tmp = ''
        if management_network_bond:
            interfaces_content += templates['iface_bonding'] % {'iface': management_network_bond, 'bond': 'bond0'}
            aliases_content_tmp += 'alias bond0 bonding\n'
        if service_network_bond:
            interfaces_content += templates['iface_bonding'] % {'iface': service_network_bond, 'bond': 'bond1'}
            aliases_content_tmp += 'alias bond1 bonding\n'
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
        aliases_content += aliases_content_tmp + 'options bonding mode=1 miimon=100 max_bonds=2'
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
            if management_network_bond:
                utils.execute('ifenslave bond0 ' + management_network_bond)
            if service_network_bond:
                utils.execute('ifenslave bond1 ' + service_network_bond)

        # Wait for bonding up.
        time.sleep(10)
        return

    def _removeRepos(self):
        (stdout, stderr) = utils.execute('sed -i /precise-updates/d /etc/apt/sources.list')
        if len(stderr) > 0: return stderr
        (stdout, stderr) = utils.execute('sed -i /precise-security/d /etc/apt/sources.list')
        if len(stderr) > 0: return stderr
        (stdout, stderr) = utils.execute('sed -i /archive.ubuntu.com/d /etc/apt/sources.list')
        if len(stderr) > 0: return stderr
        (stdout, stderr) = utils.execute('rm /etc/apt/sources.list.d/stackops.list', check_exit_code=False)
        (stdout, stderr) = utils.execute('apt-get -y update', check_exit_code=False)
        return ''


    def _installDeb(self, name, interactive=True):
        if interactive:
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
#            f.write('LoadPlugin "interface"\n')
#            f.write('LoadPlugin "cpu"\n')
#            f.write('LoadPlugin "memory"\n')
#            f.write('LoadPlugin "df"\n')
#            f.write('LoadPlugin "disk"\n')
#            f.write('LoadPlugin "vmem"\n')
#            f.write('LoadPlugin "swap"\n')
            if configType & 8 == 8:
                f.write('# compute node specific\n')
                f.write('LoadPlugin "libvirt"\n')
#            if configType & 2 == 2:
#                f.write('# network node specific\n')
#                f.write('LoadPlugin "iptables"\n')
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

#            f.write('<Plugin "interface">\n')
#            f.write('  Interface "lo"\n')
#            f.write('  IgnoreSelected true\n')
#            f.write('</Plugin>\n')

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
        try:
            (stdout, stderr) = self._installDeb('xymon-client', interactive=False)
            if len(stderr) > 0: return stderr
            utils.execute("sed -i 's/127.0.0.1/%s/g' /etc/default/hobbit-client" % xymon_ip)
            utils.execute("sed -i 's/.stackops.org//g' /etc/default/hobbit-client")
            utils.execute(
                "sed -i 's/grep -v tmpfs | awk/grep -v tmpfs | grep -v nfs | awk/g' /usr/lib/hobbit/client/bin/hobbitclient-linux.sh")
            utils.execute(
                "sed -i 's/df -Pl -x iso9660/df -P -x iso9660/g' /usr/lib/hobbit/client/bin/hobbitclient-linux.sh")
            utils.execute("service hobbit-client stop; service hobbit-client start", check_exit_code=False)
            return ''
        except:
            return "Cannot install xymon-client. Does the package exists in the repository?"

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

    def _configureAuth(self, authorized_keys, component):
        if authorized_keys is None: # Only once...
            authorized_keys = self._filler.getPropertyValue(component, 'hardening', 'authorized_keys', '')
            root_pass = self._filler.getPropertyValue(component, 'hardening', 'root_password', '')
            stackops_pass = self._filler.getPropertyValue(component, 'hardening', 'stackops_password', '')
            self._publishKeys(authorized_keys, root_pass, stackops_pass)
        return authorized_keys

    def _configureNTP(self, component, ntpServer):
        if ntpServer is None: # Only once...
            ntpServer = self._filler.getPropertyValue(component, 'infrastructure', 'ntp_server',
                'ntp.ubuntu.com')
            self._configureNTPClient(ntpServer)
        return ntpServer

    def _configureXymonAgent(self, component, xymon_server):
        result = ''
        if xymon_server is None: # Only once...
            xymon_server = self._filler.getPropertyValue(component, 'monitoring', 'xymon_server', '')
            if len(xymon_server) > 0:
                result = self._configureXymonServer(xymon_server)
        return xymon_server, result

    def _configureCollectdAgent(self, collectd_listener, component):
        if collectd_listener is None: # Only once...
            self._installDeb('collectd-core',interactive=False)
            collectd_listener = self._filler.getPropertyValue(component, 'monitoring', 'collectd_listener',
                'localhost')
            try:
                if not os.path.exists('/var/lib/collectd/rrd'):
                    utils.execute('mkdir /var/lib/collectd/rrd', check_exit_code=False)
                utils.execute('ln -s /var/lib/collectd/rrd /var/www/rrd', check_exit_code=False)
            except Exception:
                raise Exception("Cannot create symbolic link to rrd folder")
        return collectd_listener

    def importConfiguration(self, xml):
        """
        Import the configuration from the XML definition file, and configure the selected nodes.
        You must be root to execute this method
        """
        if getpass.getuser() == 'root':
            self._blacklistFb()
            result = self._removeRepos()
            if len(result) > 0: return result
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
                # One time configuration
                authorized_keys = self._configureAuth(authorized_keys, component)
                ntpServer = self._configureNTP(component, ntpServer)
                (xymon_server, result) = self._configureXymonAgent(component, xymon_server)
                if len(result) > 0: return result
                collectd_listener = self._configureCollectdAgent(collectd_listener, component)
                if component.get_name() == 'controller':
                    configType |= 1
                    # Install database
                    self._mysqlMasterConfig.write(component)
                    result = self._mysqlMasterConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install rabbitmq
                    self._rabbitMasterConfig.write(component)
                    result = self._rabbitMasterConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install keystone
                    self._keystoneConfig.write(component)
                    result = self._keystoneConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install glance
                    self._glanceConfig.write(component)
                    result = self._glanceConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install Nova-Api
                    self._novaApiConfig.write(component)
                    result = self._novaApiConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install Nova-Scheduler
                    self._novaSchedulerConfig.write(component)
                    result = self._novaSchedulerConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install Nova-NoVNCProxy
                    self._novaVncProxyConfig.write(component)
                    result = self._novaVncProxyConfig.install(hostname)
                    if len(result) > 0: return result

                    # Install Horizon

                    # Configure Horizon
                    use_horizon = self._filler.getPropertyValue(component, 'horizon', 'enabled', 'true') == 'true'
                    if use_horizon:
                        self._horizonConfig.write(component)
                        result = self._horizonConfig.install(hostname)
                        if len(result) > 0: return result

                    # Configure Portal
                    use_portal = self._filler.getPropertyValue(component, 'portal', 'enabled', 'true') == 'true'
                    if use_portal:
                        self._portalConfig.write(component)
                        result = self._portalConfig.install(hostname)
                        if len(result) > 0: return result

                    # If we have to use Nexenta, install nova-volume for nexenta here
                    use_nexenta = self._filler.getPropertyValue(component, 'nexenta_san', 'use_nexenta',
                        'false') == 'true'
                    if use_nexenta:
                        self._nexentaVolumeConfig.write(component)
                        result = self._nexentaVolumeConfig.install(hostname)
                        if len(result) > 0: return result
                    use_nfs = self._filler.getPropertyValue(component, 'nas', 'use_nas',
                        'false') == 'true'
                    if use_nfs:
                        self._qemuVolumeConfig.write(component)
                        result = self._qemuVolumeConfig.install(hostname)
                        if len(result) > 0: return result
                        # Is a Compute?
                if component.get_name() == 'compute':
                    configType |= 8
                    self._configureLinkAggregation(management_network_bond=None,service_network_bond=None)
                    self._novaComputeConfig.write(component)
                    result = self._novaComputeConfig.install(hostname)
                    if len(result) > 0: return result
                    # Is a Network?
                if component.get_name() == 'network':
                    configType |= 2
                    self._novaNetworkConfig.write(component)
                    result = self._novaNetworkConfig.install(hostname)
                    if len(result) > 0: return result
                    # Is a Linux LVM Volume?
                if component.get_name() == 'volume':
                    use_nexenta = self._filler.getPropertyValue(component, 'nexenta_san', 'use_nexenta',
                        'false') == 'true'
                    use_nfs = self._filler.getPropertyValue(component, 'nas', 'use_nas',
                        'false') == 'true'
                    if not use_nexenta and not use_nfs:
                        configType |= 4
                        self._novaVolumeLinuxLVMConfig.write(component)
                        result = self._novaVolumeLinuxLVMConfig.install(hostname)
                        if len(result) > 0: return result
# Add the rest of the components here...
#
#
#
# configType = 15, single node
# configType = 7, dual node controller
# configType = 1, 2, 4 multinode
# configType = 8 dual o multinode (compute node)
                self._createCollectdConfigFile(configType,collectd_listener)
                utils.execute('service collectd restart')
            return ''
        else:
            return 'You should run this program as super user.'

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

