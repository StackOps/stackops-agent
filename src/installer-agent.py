import sys, json
import StringIO
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from datetime import datetime

import StackOpssubs

import configuration

target = "installer.stackops.org"

#main server resource
class Root(resource.Resource):

    _configurator = configuration.Configurator()
        
    def render_GET(self, request):
        xml = self._configurator.detectConfiguration()
        output = StringIO.StringIO()
        xml.export(output,0)
        str = '<html>'
        str = str + '<head>'
        str = str + '<title>Welcome to StackOps Installer</title>'
        str = str + '</head>'
        str = str + '<body>'
        str = str + '<h1>Redirecting to StackOps Assistant...</h1>'
        str = str + '<div style="display:none">'
        str = str + '<form name="autoform" id="autoform" action="http://' +  target +'/stackops/install/wizard" method="post" >'
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

        return str

    def render_POST(self, request):
        try:
            str = 'This is a POST!'
            return str
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
            strio = StringIO.StringIO()
            strio.write(str)
            strio.seek(0)
            xml = StackOpssubs.parse(strio)
            self._configurator.importConfiguration(xml)
            return 'OK!'
        except:
            er=log.err()
            request.setResponseCode(500)
            return er

class PageNotFoundError(resource.Resource):

    def render_GET(self, request):
        return 'Page Not Found!'

#to make the process of adding new views less static
VIEWS = {
    'configuration': GetConfiguration()
}

if __name__ == '__main__':
    
    s = len(sys.argv)
    print s
    port = 8000
    if (s==3) :
        port = int(sys.argv[1])
        target = sys.argv[2]
    root = Root()
    for viewName, className in VIEWS.items():
        #add the view to the web service
        root.putChild(viewName, className)
    log.startLogging(sys.stdout)
    log.msg('Starting server: %s' %str(datetime.now()))
    server = server.Site(root)
    reactor.listenTCP(port, server)
    reactor.run()
