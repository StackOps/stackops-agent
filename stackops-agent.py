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
from twisted.internet import reactor, threads
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from datetime import datetime

import StackOpssubs

import configuration

import utils

import status

_target = 'installer.stackops.org'
#_target = 'installer.qa.stackops.org/stackops'
_port = 8888
_status_file = '/etc/nova/CONFIG_STATUS'

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
    str += '<head>'
    str += '<title>Welcome to StackOps Smart Installer</title>'
    str += '</head>'
    str += '<body>'
    str += 'Installation completed. Node ready. Please wait...<br/>'
    str += '<script type="text/javascript">'
    str += 'window.location = "http://' + _target + '/install/cloudlist"'
    str += '</script>'
    str += '</html>'
    return str

def showError(txt):
    str = '<html>'
    str += '<head>'
    str += '<title>ERROR!</title>'
    str += '</head>'
    str += '<body>'
    str += txt.replace("\n","<br />\n")
    str += '</html>'
    return str


class ThreadedResource(resource.Resource):

    def render_POST(self, request):
        d = threads.deferToThread(self.POST, request)
        d.addCallback(lambda s: (request.write(s), request.finish()))
        return server.NOT_DONE_YET

    def render_GET(self, request):
        d = threads.deferToThread(self.GET, request)
        d.addCallback(lambda s: (request.write(s), request.finish()))
        return server.NOT_DONE_YET

#main server resource
class Root(ThreadedResource):

    _configurator = configuration.Configurator()
        
    def GET(self, request):
        xml = self._configurator.detectConfiguration()
        output = StringIO.StringIO()
        xml.export(output,0)
        str = '<html>'
        str += '<head>'
        str += '<title>Welcome to StackOps Smart Installer</title>'
        str += '</head>'
        str += '<body>'
        str += 'Redirecting to StackOps Smart Installer Assistant...<br/>'
        str += '<div style="display:none">'
        str += '<form name="autoform" id="autoform" action="http://' + _target + '/entrypoint" method="post" >'
        str += '<textarea name="xml" id="xml">'
        str += output.getvalue()
        str += '</textarea>'
        str += '<input type="text" name="nodeaddress" id="nodeaddress" value=""/>'
        str += '</div>'
        str += '</body>'
        str += '<script type="text/javascript">'
        str += 'document.getElementById("nodeaddress").value=document.location.href;'
        str += 'document.autoform.submit();'
        str += '</script>'
        str += '</html>'
        return str

    def POST(self, request):
        try:
            with open(_status_file, 'w') as f:
                f.write('CONFIGURING')
            str = request.args['sysinfo'][0]
            log.msg(str)
            result = importConfiguration(self._configurator,str)
            if len(result)==0:
                with open(_status_file, 'w') as f:
                    f.write('READY')
                return showConfigDone()
            else:
                os.remove(_status_file)
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

class GetConfiguration(ThreadedResource):

    _configurator = configuration.Configurator()
    
    def GET(self, request):
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

    def POST(self, request):
        try:
            with open(_status_file, 'w') as f:
                f.write('CONFIGURING')
            str = request.content.read()
            log.msg(str)
            result = importConfiguration(self._configurator,str)
            if len(result)==0:
                with open(_status_file, 'w') as f:
                    f.write('READY')
                return showConfigDone()
            else:
                os.remove(_status_file)
                request.setResponseCode(500)
                return showError(result)
        except:
            er=log.err()
            request.setResponseCode(500)
            return er

class GetTermination(ThreadedResource):

    def GET(self, request):
        try:
            log.msg('Request: TERMINATION')
            t = threading.Thread(target=terminate)
            t.start()
            return 'Installer agent will terminate in 10 seconds...'
        except:
            er = log.err()
            request.setResponseCode(500)
            return er

    def POST(self, request):
        self.render_GET(request)
        
class PageNotFoundError(ThreadedResource):

    def GET(self, request):
        return 'Page Not Found!'

class GetStatusAPI(ThreadedResource):

    def GET(self, request):
        request.setHeader('content-type', 'text/xml')
        return status.get_xml_status()

#to make the process of adding new views less static
VIEWS = {
    'configuration': GetConfiguration(),
    'termination': GetTermination(),
    'status': GetStatusAPI(),
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
    site = server.Site(root)
    reactor.listenTCP(_port, site)
    try:
        if 'CONFIGURING' in open(_status_file).read():
            os.remove(_status_file)
    except:
        pass
    reactor.run()
