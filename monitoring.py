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
Created on Aug 1 sep, 2012

@author: Diego Parrilla
"""
import getpass
import shutil
import os
import utils

from configuration import Config

class MonitoringConfig(Config):
    def __init__(self):
        """
        Constructor
        """

    def _configureXymonAgent(self):
        result = None
        xymon_server = self.monitoring_xymon_server
        try:
            self._installDeb('xymon-client', interactive=False)
            utils.execute("sed -i 's/127.0.0.1/%s/g' /etc/default/hobbit-client" % xymon_server)
            utils.execute("sed -i 's/.stackops.org//g' /etc/default/hobbit-client")
            utils.execute(
                "sed -i 's/grep -v tmpfs | awk/grep -v tmpfs | grep -v nfs | awk/g' /usr/lib/hobbit/client/bin/hobbitclient-linux.sh")
            utils.execute(
                "sed -i 's/df -Pl -x iso9660/df -P -x iso9660/g' /usr/lib/hobbit/client/bin/hobbitclient-linux.sh")
            utils.execute("service hobbit-client stop; service hobbit-client start", check_exit_code=False)
        except Exception as e:
            result = "Cannot install xymon-client. Does the package exists in the repository? %s" % e
        return result

    def _configureCollectdAgent(self):
        self._installDeb('collectd-core', interactive=False)
        collectd_listener = self.monitoring_collectd_listener
        mngmt_iface = 'eth0'
        if hasattr(self, 'interfaces_management_interface'):
            mngmt_iface = self.interfaces_management_interface
        singlenode = (self.whatIsMyIp(mngmt_iface) == collectd_listener)
        if self.component_name == 'controller':
            try:
                if not os.path.exists('/var/lib/collectd/rrd'):
                    os.makedirs('/var/lib/collectd/rrd')
                if not os.path.exists('/var/www/rrd'):
                    os.makedirs('/var/www/rrd')
                utils.execute('ln -s /var/lib/collectd/rrd /var/www/rrd', check_exit_code=False)
            except Exception as e:
                return "Cannot create symbolic link to rrd folder:%s" % e
        path = '/etc/collectd'
        filename = 'collectd.conf'
        try:
            if not os.path.exists(path):
                return "Directory " + path + " does not exists"
        except Exception:
            return "Error reading directory " + path
        try:
            f = open('%s/%s' % (path, filename), 'w')
            f.write('# This is an automatically generated file by stackops\n')
            f.write('# Change the parameters manually at your own risk\n')
            f.write('FQDNLookup true\n')
            f.write('\n')
            f.write('LoadPlugin "logfile"\n')
            f.write('LoadPlugin "network"\n')
            f.write('\n')
            if self.component_name == 'controller':
                f.write('# Server configuration\n')
                f.write('LoadPlugin "rrdtool"\n')
                f.write('\n')
            f.write('# Client configuration\n')
            if self.component_name == 'compute' or singlenode:
                f.write('# compute node specific\n')
                f.write('LoadPlugin "libvirt"\n')
            f.write('\n')
            f.write('<Plugin "network">\n')
            if self.component_name == 'controller':
                f.write('  Listen "' + collectd_listener + '"\n')
            f.write('  Server "' + collectd_listener + '"\n')
            f.write('</Plugin>\n')
            f.write('\n')
            if self.component_name == 'controller':
                f.write('<Plugin rrdtool>\n')
                f.write('  DataDir "/var/lib/collectd/rrd"\n')
                f.write('</Plugin>\n')
                f.write('\n')
            if self.component_name == 'compute' or singlenode:
                f.write('<Plugin "libvirt">\n')
                f.write('  HostnameFormat uuid\n')
                f.write('</Plugin>\n')
            f.close()
        except Exception:
            return "Error writing file. %s/%s" % (path, filename)
        utils.execute('service collectd restart', check_exit_code=False)
        return

    def write(self, xmldoc):
        setattr(self, 'component_name', xmldoc.get_name())
        for i in xmldoc.get_service():
            service_name = i.get_type()
            for j in i.get_property():
                property_name = j.get_name()
                setattr(self, "%s_%s" % (service_name, property_name), j.get_value())
        return

    def install(self, hostname):
        """
        Install all stuff needed to configure monitoring
        """
        result = None
        try:
            if getpass.getuser() == 'root':
                # Install packages for component
                self.installPackages()
                if hasattr(self, 'monitoring_xymon_server') and len(self.monitoring_xymon_server) > 0:
                    result = self._configureXymonAgent()
                    if result is not None:
                        return result
                if hasattr(self, 'monitoring_collectd_listener') and len(self.monitoring_collectd_listener) > 0:
                    result = self._configureCollectdAgent()
                    if result is not None:
                        return result
        except  Exception as inst:
            import traceback
            traceback.print_exc()
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        """
        RabbitMQ uninstall process
        """
        utils.execute("apt-get -y --purge remove collectd-core xymon-client", check_exit_code=False)
        utils.execute("apt-get -y clean", check_exit_code=False)
        shutil.rmtree('/var/lib/collectd/rrd', ignore_errors=True)
        shutil.rmtree('/var/www/rrd', ignore_errors=True)
        return

    def installPackages(self):
        return
