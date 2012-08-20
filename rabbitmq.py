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


