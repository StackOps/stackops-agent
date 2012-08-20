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

        utils.execute("service glance-api stop && service glance-registry stop", check_exit_code=False)

        if self.glance_mount_type == 'local':
            utils.execute('rm -fr /var/lib/glance/images', check_exit_code=False)
            utils.execute('mkdir -p /var/lib/glance/images', check_exit_code=False)
            utils.execute('chown glance:glance -R /var/lib/glance/images')
        if self.glance_mount_type == 'nfs':
            utils.execute('mkdir -p /var/lib/glance/images', check_exit_code=False)
            # configure NFS mount
            mpoint = '%s %s nfs %s 0 0' % (
                self.glance_mount_point, '/var/lib/glance/images', self.glance_mount_parameters)
            utils.execute("sed -i 's#%s##g' /etc/fstab" % mpoint)
            utils.execute('echo "\n%s" >> /etc/fstab' % mpoint)
            # mount NFS remote
            utils.execute('mount -a')
            utils.execute('chown glance:glance -R /var/lib/glance/images')

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


