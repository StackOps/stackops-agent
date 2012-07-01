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
import urllib
import urllib2


from install import Filler


class MySQLConfigTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testInstall(self):
        c =configuration.MySQLMasterConfig()
        c.mysql_root_password = 'stackops'
        c.installPackages()

    def testConfigure(self):
        url = 'http://127.0.0.1:8888'
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        values = {'sysinfo' : 'Michael Foord' }
        headers = { 'User-Agent' : user_agent }

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        the_page = response.read()

        self.assertTrue(the_page)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()