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
import getpass

import flags
import install
import utils

class Config(object):
    '''
    classdocs
    '''

    _parameterList = set(['param1','param2','param3','param4'])
    _filename = "nofilename"
 
    _flags = flags.Flags()
    _filler = install.Filler()
    
    def __init__(self):
        '''
        Constructor
        '''
     
    def _readFile(self, filename):
        return self._flags.readFile("/etc/nova", filename)
        
    def _writeFile(self, filename, parameters):
        self._flags.writeFile("/etc/nova", filename, parameters)
    
    def readXML(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def writeXML(self):
        raise NotImplementedError( "Should have implemented this" )
                
    def install(self):
        raise NotImplementedError( "Should have implemented this" )
    
    def checkInstallation(self):
        # Read the configuration file
        try:
            parameters = self._readFile(self._filename)
        except Exception:
            # The file does not exists. No installation whatsoever
            return False
        
        # Exists the configuration file, but empty
        if (len(self._filename)<1):
            return False
        
        # Check if the full list of needed parameters are in the config file
        return self._parameterList.issubset(set(parameters.keys()))
    
    def read(self):
        raise NotImplementedError( "Should have implemented this" )
            
    def write(self,xmldoc):
        raise NotImplementedError( "Should have implemented this" )

# Parse connection string
    def _parseConnectionString(self, conn):
        con = conn.split('://')
        connect = con[1].split('@')
        userandpass = connect[0].split(':')
        user = userandpass[0]
        password = userandpass[1]
        hostandschema = connect[1].split('/')
        hostandport = hostandschema[0].split(':')
        host = hostandport[0]
        port = hostandport[1]
        schema = hostandschema[1]

        parameters = {'user':user, 'password':password, 'host':host, 'port':port, 'schema':schema}
        return parameters
        


class ControllerConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['network_size', 
                          'verbose', 
                          'rabbit_host', 
                          'fixed_range', 
                          'sql_connection', 
                          'ec2_dmz_host', 
                          'state_path', 
                          'auth_driver', 
                          'network_manager', 
                          'ec2_host', 
                          's3_dmz', 
                          'logdir', 
                          's3_host', 
                          'nodaemon'])

    _filename = "nova-controller.conf"

    def __init__(self):
        '''
        Constructor
        '''
# Check if there is an existing configuration file for the Controller
    def checkInstallation(self):
        check = super(ControllerConfig, self).checkInstallation()
        return check
        
# Read the parameters (if possible) and creates the config XML
    def read(self):
        controller = None
        if (self.checkInstallation()):
            # A configuration exists, read it and populate XML
            parameters = self._readFile(self._filename)
            
            # generic parameters
            verbose = parameters['verbose']
            nodaemon = parameters['nodaemon']
            
            # Authentication driver
            auth_driver = parameters['auth_driver']
    
            # log directory
            logdir = parameters['logdir']

            # state directory type
            state_path = parameters['state_path']

            # mysql database
            conn_params = self._parseConnectionString(parameters['sql_connection'])
            mysql_username = conn_params['user']
            mysql_password = conn_params['password']
            mysql_hostname = conn_params['host']
            mysql_port = conn_params['port']
            mysql_schema = conn_params['schema']

            # S3 Images service host
            s3_host = parameters['s3_host']
            s3_dmz = parameters['s3_dmz']

            # RabbitMQ broker host
            rabbit_host = parameters['rabbit_host']

            # EC2 API Listen port
            ec2_host = parameters['ec2_host']
            ec2_dmz_host = parameters['ec2_dmz_host']

            # network configuration
            network_manager = parameters['network_manager']        
            network_fixed_range = parameters['fixed_range']
            network_size = parameters['network_size']
#            flat_interface = parameters['flat_interface']
            
            controller = self._filler.populateController(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            controller = None
        
        return controller

# Write the parameters (if possible) from the xml file
    def write(self,xmldoc):
        controller = xmldoc
        
        verbose = self._filler.getPropertyValue(controller, 'generic', 'verbose')
        nodaemon = self._filler.getPropertyValue(controller, 'generic', 'nodaemon')

        network_manager = self._filler.getPropertyValue(controller,'network','type')
        fixed_range = self._filler.getPropertyValue(controller,'network','fixed_range')
        network_size = self._filler.getPropertyValue(controller,'network','network_size')
#        flat_interface = self._filler.getPropertyValue(controller,'network_manager','flat_interface')

        mysql_username = self._filler.getPropertyValue(controller, 'database', 'username')
        mysql_password = self._filler.getPropertyValue(controller, 'database', 'password')
        mysql_host = self._filler.getPropertyValue(controller, 'database', 'host')
        mysql_port = self._filler.getPropertyValue(controller, 'database', 'port')
        mysql_schema = self._filler.getPropertyValue(controller, 'database', 'schema')
        sql_connection = 'mysql://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_schema

        auth_driver = self._filler.getPropertyValue(controller, 'authentication', 'driver')

        logdir = self._filler.getPropertyValue(controller, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(controller, 'state', 'path')

        s3_host = self._filler.getPropertyValue(controller, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(controller, 's3', 'dmz')
        
        rabbit_host = self._filler.getPropertyValue(controller, 'rabbitmq', 'hostname')

        ec2_hostname = self._filler.getPropertyValue(controller, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(controller, 'ec2', 'dmz')

        parameters = {'verbose':verbose, 
                      'nodaemon':nodaemon,
                      'network_manager':network_manager, 
                      'fixed_range':fixed_range, 
                      'network_size':network_size,
                      'sql_connection':sql_connection, 
                      'auth_driver':auth_driver, 
                      'logdir':logdir, 
                      'state_path':state_path,                       
                      's3_host':s3_host, 
                      's3_dmz':s3_dmz, 
                      'rabbit_host':rabbit_host, 
                      'ec2_host':ec2_hostname,
                      'ec2_dmz_host':ec2_dmz}
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc):
        
        if (getpass.getuser()=='root'):
            mysql_pass = self._filler.getPropertyValue(xmldoc, 'database', 'password')
    
            # now let's start with the hard part
            utils.execute('apt-cdrom add',None,None,False)
            utils.execute('apt-get update',None,None,False)
            
            utils.execute('echo mysql-server-5.1 mysql-server/root_password password ' + mysql_pass + ' | debconf-set-selections')
            utils.execute('echo mysql-server-5.1 mysql-server/root_password_again password ' + mysql_pass + ' | debconf-set-selections')
            utils.execute('echo mysql-server-5.1 mysql-server/start_on_boot boolean true')
    
            utils.execute('mount /dev/cdrom /cdrom',None,None,False)
            utils.execute('apt-get install -y mysql-server')
    
            utils.execute("sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf")
            utils.execute('service mysql restart')
    
            utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "DROP DATABASE nova;"''', None,None,False)
            utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "CREATE DATABASE nova;"''')
            utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"''')
            utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "SET PASSWORD FOR 'root'@'%' = PASSWORD('nova');"''')
    
            utils.execute('mount /dev/cdrom /cdrom',None,None,False)
            utils.execute('DEBIAN_FRONTEND=noninteractive apt-get install -y rabbitmq-server')
            
            utils.execute('killall dnsmasq',None,None,False)
            utils.execute('rm -fr /root/creds')
            utils.execute('mkdir /root/creds')
            
            # nova.conf in bin linked to controller info
            utils.execute('rm /var/lib/nova/bin/nova.conf')
            utils.execute('ln -s /etc/nova/nova-controller.conf /var/lib/nova/bin/nova.conf')
            
            # create the database        
            utils.execute('/var/lib/nova/bin/nova-manage db sync')
            # create an admin user called 'admin'
            utils.execute('/var/lib/nova/bin/nova-manage user admin admin admin admin')
            # create a project called 'admin' with project manager of 'admin'
            utils.execute('/var/lib/nova/bin/nova-manage project create admin admin')
            # export environment variables for project 'admin' and user 'admin'
            utils.execute('/var/lib/nova/bin/nova-manage project env admin admin /root/creds/novarc')
            # create a small network
            utils.execute('/var/lib/nova/bin/nova-manage network create 10.0.0.0/8 1 32')
    
            # enable controller components
            utils.execute('mv /etc/init/nova-ajax-console-proxy.conf.disabled /etc/init/nova-ajax-console-proxy.conf')
            utils.execute('mv /etc/init/nova-api.conf.disabled /etc/init/nova-api.conf')
            utils.execute('mv /etc/init/nova-scheduler.conf.disabled /etc/init/nova-scheduler.conf')
            utils.execute('mv /etc/init/nova-objectstore.conf.disabled /etc/init/nova-objectstore.conf')
    
            # start controller components
            utils.execute('start nova-ajax-console-proxy')
            utils.execute('start nova-api')
            utils.execute('start nova-scheduler')
            utils.execute('start nova-objectstore')

        return

class ComputeConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['network_size', 
                          'verbose', 
                          'rabbit_host', 
                          'fixed_range', 
                          'sql_connection', 
                          'ec2_dmz_host', 
                          'state_path', 
                          'auth_driver', 
                          'network_manager', 
                          'ec2_host', 
                          's3_dmz', 
                          'logdir', 
                          's3_host', 
                          'nodaemon',
                          'libvirt_type'])

    _filename = "nova-compute.conf"

    def __init__(self):
        '''
        Constructor
        '''
# Check if there is an existing configuration file for the Controller
    def checkInstallation(self):
        check = super(ComputeConfig, self).checkInstallation()
        return check
        
# Read the parameters (if possible) and creates the config XML
    def read(self):
        compute = None
        if (self.checkInstallation()):
            # A configuration exists, read it and populate XML
            parameters = self._readFile(self._filename)
            
            # generic parameters
            verbose = parameters['verbose']
            nodaemon = parameters['nodaemon']
            
            # Authentication driver
            auth_driver = parameters['auth_driver']
    
            # log directory
            logdir = parameters['logdir']

            # state directory type
            state_path = parameters['state_path']

            # mysql database
            conn_params = self._parseConnectionString(parameters['sql_connection'])
            mysql_username = conn_params['user']
            mysql_password = conn_params['password']
            mysql_hostname = conn_params['host']
            mysql_port = conn_params['port']
            mysql_schema = conn_params['schema']

            # S3 Images service host
            s3_host = parameters['s3_host']
            s3_dmz = parameters['s3_dmz']

            # RabbitMQ broker host
            rabbit_host = parameters['rabbit_host']

            # EC2 API Listen port
            ec2_host = parameters['ec2_host']
            ec2_dmz_host = parameters['ec2_dmz_host']

            # network configuration
            network_manager = parameters['network_manager']        
            network_fixed_range = parameters['fixed_range']
            network_size = parameters['network_size']
            
            # COMPUTE-NODE SPECIFIC
            # libvirt virtualization type
            libvirt_type = parameters['libvirt_type']
    
            compute = self._filler.populateCompute(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size,libvirt_type)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            compute = None
        
        return compute

# Write the parameters (if possible) from the xml file
    def write(self,xmldoc):
        verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose')
        nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon')

        network_manager = self._filler.getPropertyValue(xmldoc,'network','type')
        fixed_range = self._filler.getPropertyValue(xmldoc,'network','fixed_range')
        network_size = self._filler.getPropertyValue(xmldoc,'network','network_size')

        mysql_username = self._filler.getPropertyValue(xmldoc, 'database', 'username')
        mysql_password = self._filler.getPropertyValue(xmldoc, 'database', 'password')
        mysql_host = self._filler.getPropertyValue(xmldoc, 'database', 'host')
        mysql_port = self._filler.getPropertyValue(xmldoc, 'database', 'port')
        mysql_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema')
        sql_connection = 'mysql://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_schema

        auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver')

# NOVA-COMPUTE
        libvirt_type = self._filler.getPropertyValue(xmldoc, 'libvirt', 'type')

        logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path')

        s3_host = self._filler.getPropertyValue(xmldoc, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz')
        
        rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')

        ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')

        parameters = {'verbose':verbose, 
                      'nodaemon':nodaemon,
                      'network_manager':network_manager, 
                      'fixed_range':fixed_range, 
                      'network_size':network_size,
                      'sql_connection':sql_connection, 
                      'auth_driver':auth_driver, 
# NOVA-COMPUTE SPECIFIC
                      'libvirt_type':libvirt_type, 
                      'logdir':logdir, 
                      'state_path':state_path,                       
                      's3_host':s3_host, 
                      's3_dmz':s3_dmz, 
                      'rabbit_host':rabbit_host, 
                      'ec2_host':ec2_hostname,
                      'ec2_dmz_host':ec2_dmz}
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc):

        # enable libvirt-bin
        utils.execute('mv /etc/init/libvirt-bin.conf.disabled /etc/init/libvirt-bin.conf',None,None,False)
        
        # enable controller components
        utils.execute('mv /etc/init/nova-compute.conf.disabled /etc/init/nova-compute.conf',None,None,False)

        # start libvirt components
        utils.execute('start libvirt-bin')

        # start compute components
        utils.execute('start nova-compute')

        return

class NetworkConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['network_size', 
                          'verbose', 
                          'rabbit_host', 
                          'fixed_range', 
                          'sql_connection', 
                          'ec2_dmz_host', 
                          'state_path', 
                          'auth_driver', 
                          'network_manager', 
                          'ec2_host', 
                          's3_dmz', 
                          'logdir', 
                          's3_host', 
                          'nodaemon',
                          'dhcpbridge_flagfile',
                          'dhcpbridge',
                          'routing_source_ip'])

    _filename = "nova-network.conf"

    def __init__(self):
        '''
        Constructor
        '''
# Check if there is an existing configuration file for the Network
    def checkInstallation(self):
        check = super(NetworkConfig, self).checkInstallation()
        return check
        
# Read the parameters (if possible) and creates the config XML
    def read(self):
        network = None
        if (self.checkInstallation()):
            # A configuration exists, read it and populate XML
            parameters = self._readFile(self._filename)
            
            # generic parameters
            verbose = parameters['verbose']
            nodaemon = parameters['nodaemon']
            
            # Authentication driver
            auth_driver = parameters['auth_driver']
    
            # log directory
            logdir = parameters['logdir']

            # state directory type
            state_path = parameters['state_path']

            # mysql database
            conn_params = self._parseConnectionString(parameters['sql_connection'])
            mysql_username = conn_params['user']
            mysql_password = conn_params['password']
            mysql_hostname = conn_params['host']
            mysql_port = conn_params['port']
            mysql_schema = conn_params['schema']

            # S3 Images service host
            s3_host = parameters['s3_host']
            s3_dmz = parameters['s3_dmz']

            # RabbitMQ broker host
            rabbit_host = parameters['rabbit_host']

            # EC2 API Listen port
            ec2_host = parameters['ec2_host']
            ec2_dmz_host = parameters['ec2_dmz_host']

            # NETWORK-NODE SPECIFIC
            # dhcpbridge config
            dhcpbridge_flagfile = parameters['dhcpbridge_flagfile']
            dhcpbridge = parameters['dhcpbridge']

            # Routing source IP
            routing_source_ip = parameters['routing_source_ip']
            
            # network configuration
            network_manager = parameters['network_manager']        
            network_fixed_range = parameters['fixed_range']
            network_size = parameters['network_size']
#            flat_interface = parameters['flat_interface']
            
            network = self._filler.populateNetworkNode(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size,dhcpbridge_flagfile,dhcpbridge,routing_source_ip)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            network = None
        
        return network

# Write the parameters (if possible) from the xml file
    def write(self,xmldoc):

        verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose')
        nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon')
# NOVA-NETWORK SPECIFIC
        dhcpbridge = self._filler.getPropertyValue(xmldoc, 'dhcpbridge', 'process')
        dhcpbridge_flagfile = self._filler.getPropertyValue(xmldoc, 'dhcpbridge', 'file')
        routing_source_ip = self._filler.getPropertyValue(xmldoc, 'routing_source', 'ip')
        network_manager = self._filler.getPropertyValue(xmldoc,'network','type')
        fixed_range = self._filler.getPropertyValue(xmldoc,'network','fixed_range')
        network_size = self._filler.getPropertyValue(xmldoc,'network','network_size')
#        flat_interface = self._filler.getPropertyValue(controller,'network_manager','flat_interface')

        mysql_username = self._filler.getPropertyValue(xmldoc, 'database', 'username')
        mysql_password = self._filler.getPropertyValue(xmldoc, 'database', 'password')
        mysql_host = self._filler.getPropertyValue(xmldoc, 'database', 'host')
        mysql_port = self._filler.getPropertyValue(xmldoc, 'database', 'port')
        mysql_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema')
        sql_connection = 'mysql://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_schema
        auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver')
        logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path')
        s3_host = self._filler.getPropertyValue(xmldoc, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz')
        rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')
        ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')

        parameters = {'verbose':verbose, 
                      'nodaemon':nodaemon,
# NOVA-NETWORK SPECIFIC
                      'dhcpbridge':dhcpbridge,
                      'dhcpbridge_flagfile':dhcpbridge_flagfile, 
                      'routing_source_ip':routing_source_ip, 
                      'network_manager':network_manager, 
                      'fixed_range':fixed_range, 
                      'network_size':network_size,
#                      'flat_interface':flat_interface,                      
                      'sql_connection':sql_connection, 
                      'auth_driver':auth_driver, 
                      'logdir':logdir, 
                      'state_path':state_path,                       
                      's3_host':s3_host, 
                      's3_dmz':s3_dmz, 
                      'rabbit_host':rabbit_host, 
                      'ec2_host':ec2_hostname,
                      'ec2_dmz_host':ec2_dmz}
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc):
        # enable network components
        utils.execute('mv /etc/init/nova-network.conf.disabled /etc/init/nova-network.conf',None,None,False)

        # start network components
        utils.execute('start nova-network')

        return


class Configurator(object):
    '''
    classdocs
    '''
    
    _controllerConfig = ControllerConfig()
    _computeConfig = ComputeConfig()
    _networkConfig = NetworkConfig()
    _filler = install.Filler();

    def __init__(self):
        '''
        Constructor
        '''
    # Check the existing configuration files        
    def detectConfiguration(self):
        cloud = None
        # Is a Controller?
        if (self._controllerConfig.checkInstallation()):
            controller = self._controllerConfig.read()
            cloud = self._filler.populateCloud(cloud, controller, None)

        # Is a Component?
        if (self._computeConfig.checkInstallation()):
            compute = self._computeConfig.read()
            cloud = self._filler.populateCloud(cloud, compute, None)
            
        # Is a Network?
        if (self._networkConfig.checkInstallation()):
            network = self._networkConfig.read()
            cloud = self._filler.populateCloud(cloud, network, None)

        # Add the rest of the components here...
        #
        #
        #
        
        node = self._filler.createNode(cloud)
        return node
    
    # Parse XML and extract the component configuration chosen        
    def importConfiguration(self,xml):       
        
        for component in xml.get_cloud().get_component():
            # Is a Controller?
            if (component.get_name()=='controller'):
                self._controllerConfig.write(component)
                self._controllerConfig.install(component)
    
            # Is a Compute?
            if (component.get_name()=='compute'):
                self._computeConfig.write(component)
                self._computeConfig.install(component)

            # Is a Network?
            if (component.get_name()=='network'):
                self._networkConfig.write(component)
                self._networkConfig.install(component)
            
        # Add the rest of the components here...
        #
        #
        #
        
        return
    
        


            
