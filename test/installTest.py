import unittest
import sys

import install

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testPopulateXML(self):
        f = install.Filler()
        f.createNode(None)
        pass

    def testPopulateController(self):
        f = install.Filler()
        node = f.populateController('root', 'nova', 'localhost', '3306', 'nova', '192.168.10.10', '8773','/services/Cloud','nova.network.manager.VlanManager','192.168.0.0/12','5000')
        node.export(sys.stdout,0)
        pass

    def testImportNode(self):
        f = install.Filler()
        node = f.importNode('test_conf.xml')
        node.export(sys.stdout,0)
        pass

class MachineTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCPUType(self):
        c = install.Machine()
        self.assertTrue(len(c.getCPUType())>0)

    def testCPUCount(self):
        c = install.Machine()
        self.assertEqual(2,c.getCPUCount())

    def testMachineType(self):
        c = install.Machine()
        self.assertEqual("x86_64",c.getMachine())
        
    def testCPUSpeed(self):
        c = install.Machine()
        self.assertTrue(len(c.getCPUSpeed())>0)

    def testMemoryAvailable(self):
        c = install.Machine()
        self.assertTrue(c.getMemoryAvailable()>0)
    
    def testInterfacesList(self):
        # now, use the function to get the 'up' interfaces array
        c = install.Machine()
        ifaces = c.getIfaceList()
        # well, what to do? print it out maybe... 
        for iface in ifaces:
            print iface
        self.assertTrue()

    def testBlockDevicesList(self):
        c = install.Machine() 
        self.assertTrue(len(c.getBlockDeviceList())>0)

class OperatingSystemTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testGetUname(self):
        c = install.OperatingSystem()
        uname = c.getUname()
        print uname[3]
        self.assertNotEqual(0,len(uname[3]))

    def testGetHostname(self):
        c = install.OperatingSystem()
        hostname = c.getHostname()
        print hostname
        self.assertNotEqual(0,len(hostname))

    def testNameserver(self):
        c = install.OperatingSystem()
        nameservers = c.getNameservers()
        print nameservers
        self.assertNotEqual(0,nameservers)

    def testNetworkConfiguration(self):
        c = install.OperatingSystem()
        nameservers = c.getNetworkConfiguration()
        print nameservers
        self.assertNotEqual(0,nameservers)

class PackageTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        c = install.Package()
        c.install_common()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()