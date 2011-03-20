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
import sys, json
import StringIO
import threading
import time
import os
import urllib
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from datetime import datetime

import StackOpssubs

import configuration

import utils

_target = 'http://installer.stackops.org/entrypoint'
_port = 8888

def terminate():
    time.sleep(10)
    log.msg("Terminating install agent... good bye!")
    utils.execute('stop stackops')
    log.msg("You should not read this message after stopping the process!")

def importConfiguration(configurator, str):
    strio = StringIO.StringIO()
    strio.write(str)
    strio.seek(0)
    xml = StackOpssubs.parse(strio)
    return configurator.importConfiguration(xml)

def showConfigDone():
    str = '<html>'
    str = str + '<head>'
    str = str + '<title>Welcome to StackOps Smart Installer</title>'
    str = str + '</head>'
    str = str + '<body>'
    str = str + 'Installation completed. Node ready.<br/>'
    str = str + '</html>'
    return str

def showError(txt):
    str = '<html>'
    str = str + '<head>'
    str = str + '<title>ERROR!</title>'
    str = str + '</head>'
    str = str + '<body>'
    str = str + txt.replace("\n","<br />\n")
    str = str + '</html>'
    return str

#main server resource
class Root(resource.Resource):

    _configurator = configuration.Configurator()
        
    def render_GET(self, request):
        xml = self._configurator.detectConfiguration()
        output = StringIO.StringIO()
        xml.export(output,0)
        str = '<html>'
        str = str + '<head>'
        str = str + '<title>Welcome to StackOps Smart Installer</title>'
        str = str + '</head>'
        str = str + '<body>'
        str = str + 'Redirecting to StackOps Assistant...<br/>'
        str = str + '<div style="display:none">'
        str = str + '<form name="autoform" id="autoform" action="' + _target + '" method="post" >'
        str = str + '<textarea name="xml" id="xml">'
        str = str + output.getvalue()
        str = str + '</textarea>'
        str = str + '<input type="text" name="nodeaddress" id="nodeaddress" value=""/>'
        str = str + '</div>'
        str = str + '</body>'
        str = str + '<script type="text/javascript">'
        str = str + 'document.getElementById("nodeaddress").value=document.location.href;'
        str = str + 'document.autoform.submit();'
        str = str + '</script>'    
        str = str + '</html>'
        return str

    def render_POST(self, request):
        try:
            str = request.args['sysinfo'][0]
            log.msg(str)
            result = importConfiguration(self._configurator,str)
            if len(result)==0:
                return showConfigDone()
            else:
                request.setResponseCode(500)
                return showError(result)
        except:
            er=log.err()
            request.setResponseCode(500)
            return er

    def getChild(self, name, request):
        if name == '':
            return self
        else:
            if name in VIEWS.keys():
                return resource.Resource.getChild(self, name, request)
            else:
                return PageNotFoundError()

class GetConfiguration(resource.Resource):

    _configurator = configuration.Configurator()
    
    def render_GET(self, request):
        try:
            log.msg('Request:')
            xml = self._configurator.detectConfiguration()
            output = StringIO.StringIO()
            xml.export(output,0)
            return output.getvalue()
        except:
            er = log.err()
            request.setResponseCode(500)
            return er

    def render_POST(self, request):
        try:
            str = request.content.read()
            log.msg(str)
            result = importConfiguration(self._configurator,str)
            if len(result)==0:
                return showConfigDone()
            else:
                request.setResponseCode(500)
                return showError(result)
        except:
            er=log.err()
            request.setResponseCode(500)
            return er

class GetTermination(resource.Resource):

    def render_GET(self, request):
        try:
            log.msg('Request: TERMINATION')
            t = threading.Thread(target=terminate)
            t.start()
            return 'Installer agent will terminate in 10 seconds...'
        except:
            er = log.err()
            request.setResponseCode(500)
            return er

    def render_POST(self, request):
        self.render_GET(request)
        
class PageNotFoundError(resource.Resource):

    def render_GET(self, request):
        return 'Page Not Found!'

#to make the process of adding new views less static
VIEWS = {
    'configuration': GetConfiguration(),
    'termination': GetTermination(),
}

if __name__ == '__main__':
    s = len(sys.argv)
    if (s==3) :
        _port = int(sys.argv[1])
        _target = sys.argv[2]
    root = Root()
    #add the views to the web service
    for viewName, className in VIEWS.items():
        root.putChild(viewName, className)
    log.startLogging(sys.stdout)
    log.msg('Starting server: %s' %str(datetime.now()))
    server = server.Site(root)
    reactor.listenTCP(_port, server)
    reactor.run()
