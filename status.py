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
Created on Nov 28, 2011

@author: German Moya
'''

from os.path import exists
from commands import getoutput
try:
    from CStringIO import StringIO
except:
    from StringIO import StringIO
from xml.sax.saxutils import escape, quoteattr
import re

from StackOps import property, service, component, cloud, node

def service_running(service_name):
    return 'start/running' in getoutput('status '+service_name)

def rabbitmq_running():
    out = getoutput('invoke-rc.d rabbitmq-server status')
    return bool(re.search(r'^Node .+ with Pid .+: running', out, re.M))

def get_test_command(service):
    if service == 'rabbitmq':
        return (rabbitmq_running, )
    return (service_running, service)

def get_node_services():
    service_list = ['nova-api', 'nova-scheduler', 'nova-consoleauth', 'nova-network', 'glance-api', 'glance-registry',
        'keystone', 'novnc', 'nova-compute', 'libvirt-bin', 'nova-volume', 'mysql']
    services_list = [service for service in service_list if exists( '/etc/init/%s.conf'%service )]
    if exists('/etc/init.d/rabbitmq-server'):
        service_list.append('rabbitmq')
    return services_list

def get_services_status():
    status = []
    for service in get_node_services():
        test_command = get_test_command(service)
        running = test_command[0](*test_command[1:])
        status.append((service, running))
    return status

def get_xml_status():
    cld = cloud()
    comp = component('status')
    cld.add_component(comp)
    serv = service('setup')
    node_status = get_node_status()
    serv.add_property(property('state', node_status))
    comp.add_service(serv)
    if node_status == 'READY':
        for name, running in get_services_status():
            serv = service(name)
            serv.add_property(property('running', ('no','yes')[running]))
            comp.add_service(serv)
    io = StringIO()
    node(cloud=cld).export(io, 0)
    return io.getvalue()

def get_node_status():
    try:
        status = open('/etc/nova/CONFIG_STATUS').read().strip()
    except:
        return 'NOT_CONFIGURED'
    if status == 'READY':
        return 'READY'
    return 'CONFIGURING'