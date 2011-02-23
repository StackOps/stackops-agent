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