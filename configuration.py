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
import inspect

@utils.singleton
class ConfigFactory(object):

    __instancesConfig = {}

    def __get_class_instance( self, kls ):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)
            if inspect.isclass(m):
                m = m()
        return m

    def get(self):
        return self.__instancesConfig

    def getConfig(self,configklass):
        if configklass in self.__instancesConfig:
            instance = self.__instancesConfig[configklass]
        else:
            instance = self.__get_class_instance(configklass)
            if instance is None:
                raise Exception("%s does not exists" % configklass)
            self.__instancesConfig[configklass] = instance
        return instance

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


class OSConfigurator(object):
    '''
    classdocs
    '''

    _bondigConfig = ConfigFactory().getConfig('bonding.BondingConfig')
    _monitoringConfig = ConfigFactory().getConfig('monitoring.MonitoringConfig')
    _mysqlMasterConfig = ConfigFactory().getConfig('mysql.MySQLMasterConfig')
    _rabbitMasterConfig = ConfigFactory().getConfig('rabbitmq.RabbitMQMasterConfig')
    _keystoneConfig = ConfigFactory().getConfig('keystone.KeystoneConfig')
    _glanceConfig =  ConfigFactory().getConfig('glance.GlanceConfig')
    _novaApiConfig = ConfigFactory().getConfig('nova.NovaApiConfig')
    _novaSchedulerConfig = ConfigFactory().getConfig('nova.NovaSchedulerConfig')
    _novaVncProxyConfig = ConfigFactory().getConfig('nova.NovaVncProxyConfig')
    _novaNetworkConfig = ConfigFactory().getConfig('nova.NovaNetworkConfig')
    _novaComputeConfig = ConfigFactory().getConfig('nova.NovaComputeConfig')
    _horizonConfig = ConfigFactory().getConfig('nova.HorizonConfig')
    _novaVolumeLinuxLVMConfig = ConfigFactory().getConfig('nova.NovaVolumeLinuxLVMConfig')
    _nexentaVolumeConfig = ConfigFactory().getConfig('nova.NexentaVolumeConfig')
    _qemuVolumeConfig = ConfigFactory().getConfig('nova.QEMUVolumeConfig')
    _portalConfig = ConfigFactory().getConfig('portal.PortalConfig')
    _filler = install.Filler();

    def __init__(self):
        '''
        Constructor
        '''

    def _addDefaultUsers(self):
        utils.execute('addgroup --system --gid 201 nova', check_exit_code=False)
        utils.execute('adduser --system --home /var/lib/nova --shell /bin/false --no-create-home --uid 201 --ingroup nova nova', check_exit_code=False)
        utils.execute('addgroup --system --gid 202 glance', check_exit_code=False)
        utils.execute('adduser --system --home /var/lib/glance --shell /bin/false --no-create-home --uid 202 --ingroup glance glance', check_exit_code=False)

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
            utils.execute("sed -i 's/%sudo.*ALL=(ALL:ALL) ALL/%sudo ALL=(ALL) NOPASSWD:ALL/g' /etc/sudoers")
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

    def _configureAuth(self, component):
        authorized_keys = self._filler.getPropertyValue(component, 'hardening', 'authorized_keys', '')
        root_pass = self._filler.getPropertyValue(component, 'hardening', 'root_password', '')
        stackops_pass = self._filler.getPropertyValue(component, 'hardening', 'stackops_password', '')
        self._publishKeys(authorized_keys, root_pass, stackops_pass)
        return

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
            # Set default users
            self._addDefaultUsers()
            first_component = True
            for component in xml.get_cloud().get_component():
                # One time configuration
                if first_component:
                    result = self._configureAuth(component)
                    if result is not None: return result
                    self._monitoringConfig.write(component)
                    result = self._monitoringConfig.install(hostname)
                    if result is not None: return result
                    self._bondigConfig.write(component)
                    result = self._bondigConfig.install()
                    if result is not None: return result
                    first_component = False
                if component.get_name() == 'controller':
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

                    # Install the test distro by default
                    install_test_distro = self._filler.getPropertyValue(component, 'generic', 'test_distro','true') == 'true'
                    if install_test_distro:
                        utils.execute('cd /var/lib/stackops; ./pubttylinuxlocal.sh', check_exit_code=False)
                if component.get_name() == 'compute':
                    self._novaComputeConfig.write(component)
                    result = self._novaComputeConfig.install(hostname)
                    if len(result) > 0: return result
                    # Is a Network?
                if component.get_name() == 'network':
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
                        self._novaVolumeLinuxLVMConfig.write(component)
                        result = self._novaVolumeLinuxLVMConfig.install(hostname)
                        if len(result) > 0: return result
            return ''
        else:
            return 'You should run this program as super user.'
