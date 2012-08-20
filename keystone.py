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
import shutil

import utils

from configuration import Config

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


