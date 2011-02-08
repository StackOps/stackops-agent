'''
Created on Jan 23, 2011

@author: stackops
'''
import unittest

import flags

class FlagsTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testReadFile(self):
        f = flags.Flags()
        parameters = f.readFile(".", "testfiles.conf")
        print parameters
        pass

    def testWriteFile(self):
        f = flags.Flags()
#        parameters = []
#        parameters.append({'parameter':'param1','value':'value1'})
#        parameters.append({'parameter':'param2','value':'value2'})
#        parameters.append({'parameter':'param3','value':''})
#        parameters.append({'parameter':'param4','value':'value4'})
        parameters = {'param1':'value1','param2':'value2','param3':'value3','param4':'value4','param5':'','param6':'value6'}
        f.writeFile(".", "testfiles.conf", parameters)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()