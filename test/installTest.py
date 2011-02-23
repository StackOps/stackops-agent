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
import os

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
        node = f.populateController('verbose', 
                                    'nodaemon', 
                                    'root', 
                                    'nova', 
                                    'mysql_host', 
                                    '3306', 
                                    'nova', 
                                    'nova.auth.dbdriver.DbDriver', 
                                    '/var/log/nova', 
                                    '/var/lib/nova', 
                                    's3_host', 
                                    's3_host_dmz', 
                                    'rabbitmq_host', 
                                    'ec2_host', 
                                    'ec2_dmz_host', 
                                    'nova.network.manager.VlanManager',
                                    '192.168.0.0/12',
                                    '5000')
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
        self.assertTrue(len(ifaces)>0)

    def testBlockDevicesList(self):
        c = install.Machine() 
        self.assertTrue(len(c.getBlockDeviceList())>0)

    def testVirtualization(self):
        iface =  os.popen2("egrep '(vmx|svm)' /proc/cpuinfo")[1].read()
        v = "False"
        if len(iface)>0:
            v =  "True"
        c = install.Machine() 
        self.assertTrue(v == c.getVirtualization())
      

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
