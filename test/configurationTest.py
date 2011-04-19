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

'''
Created on Feb 21, 2011

@author: Diego Parrilla
'''
import unittest
import sys
import configuration
import StackOps

from install import Filler


class ConfiguratorTest(unittest.TestCase):


    _filler = Filler()
    
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDetectConfiguration(self):
        c = configuration.Configurator()
        c.detectConfiguration()
        pass

    def testImportConfiguration(self):
        controller = self._filler.populateController('true','true', 'root', 'nova', '192.168.10.31', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000','true')
        cloud = StackOps.cloud()
        cloud.add_component(controller)
        node = self._filler.createNode(cloud)
        node.export(sys.stdout,0)
        c = configuration.Configurator()
        c.importConfiguration(node)
        pass

    def testCreateCollectdConfig(self):
        c = configuration.Configurator()
        c._createCollectdConfigFile(15, '192.168.10.30')
        pass

class ControllerConfigTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testCheckInstallation(self):
        c =configuration.ControllerConfig()
        self.assertTrue(c.checkInstallation())
    def testRead(self):
        c = configuration.ControllerConfig()
        self.assertTrue(c.read())
    def testWrite(self):
        c = configuration.ControllerConfig()
        filler = Filler()        
        controller = filler.populateController('true','true', 'root', 'nova', '192.168.10.31', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000','true')
        self.assertFalse(c.write(controller))

class ComputeConfigTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testCheckInstallation(self):
        c =configuration.ComputeConfig()
        self.assertTrue(c.checkInstallation())
    def testRead(self):
        c = configuration.ComputeConfig()
        self.assertTrue(c.read())
    def testWrite(self):
        c = configuration.ComputeConfig()
        filler = Filler()        
        compute = filler.populateCompute('true','true', 'root', 'nova', '192.168.10.31', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000','qemu','true','eth1','192.168.10.31','100')
        self.assertFalse(c.write(compute))

class NetworkConfigTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testCheckInstallation(self):
        c =configuration.NetworkConfig()
        self.assertTrue(c.checkInstallation())
    def testRead(self):
        c = configuration.NetworkConfig()
        self.assertTrue(c.read())
    def testWrite(self):
        c = configuration.NetworkConfig()
        filler = Filler()        
        network = filler.populateNetworkNode('true','true', 'root', 'nova', '192.168.10.31', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000','/etc/nova/nova-network.conf','/var/lib/nova/bin/nova-dhcpbridge','192.168.10.31','true','ethFLAT','ethPUBLIC')
        self.assertFalse(c.write(network))

class VolumeConfigTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testCheckInstallation(self):
        c =configuration.VolumeConfig()
        self.assertTrue(c.checkInstallation())
    def testRead(self):
        c = configuration.VolumeConfig()
        self.assertTrue(c.read())
    def testWrite(self):
        c = configuration.VolumeConfig()
        filler = Filler()        
        volume = filler.populateVolume('true','true', 'root', 'nova', '192.168.10.31', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000','true','true')
        volume.export(sys.stdout, 0)
        self.assertFalse(c.write(volume))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()