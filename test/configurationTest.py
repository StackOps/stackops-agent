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
        controller = self._filler.populateController('true','true', 'root', 'novatest', 'localhost', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000')
        cloud = StackOps.cloud()
        cloud.add_component(controller)
        node = self._filler.createNode(cloud)
        node.export(sys.stdout,0)
        c = configuration.Configurator()
        c.importConfiguration(node)
        pass

class ControllerConfigTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testParseEc2Url(self):
        c = configuration.ControllerConfig()
        self.assertTrue(c._parseEc2Url('http://192.168.10.1:4567/ServiceA/endpointB'))

    def testCheckInstallation(self):
        c =configuration.ControllerConfig()
        self.assertTrue(c.checkInstallation())

    def testRead(self):
        c = configuration.ControllerConfig()
        self.assertTrue(c.read())

    def testWrite(self):
        c = configuration.ControllerConfig()
        filler = Filler()        
        controller = filler.populateController('true','true', 'root', 'novatest', 'localhost', '3306', 'nova', 'nova.auth.dbdriver.DbDriver', '/var/log/nova', '/var/lib/nova', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', '192.168.10.31', 'nova.network.manager.VlanManager','192.168.0.0/12','5000')

        self.assertFalse(c.write(controller))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()