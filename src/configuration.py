import sys

import flags
import install
import utils
import StackOps

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


class ControllerConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['verbose',
                          'nodaemon',
                          'dhcpbridge',
                          'dhcpbridge_flagfile',
                          'network_manager'
                          'cc_host', 
                          'routing_source_ip', 
                          'sql_connection',
                          'auth_driver',
                          'libvirt_type',
                          'logdir',
                          'state_path', 
                          's3_host', 
                          'rabbit_host', 
                          'ec2_url', 
                          'fixed_range', 
                          'network_size',
                          'FAKE_subdomain',
                          'flat_interface'])
    _filename = "nova-controller.conf"

    def __init__(self):
        '''
        Constructor
        '''
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
        
# Parse connection string
    def _parseEc2Url(self, conn):
        url = conn.split('http://')
        hostanduri = url[1].split('/')
        hostandport = hostanduri[0].split(':')
        host = hostandport[0]
        port = hostandport[1]
        uritmp = hostanduri[1:]
        uri = ''
        for item in uritmp:
            uri = uri + '/' + item
        parameters = {'host':host, 'port':port, 'uri':uri}
        return parameters

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
            
            # dhcpbridge config
            dhcpbridge_flagfile = parameters['dhcpbridge_flagfile']
            dhcpbridge = parameters['dhcpbridge']

            # network configuration
            network_manager = parameters['network_manager']        
            network_fixed_range = parameters['fixed_range']
            network_size = parameters['network_size']
            flat_interface = parameters['flat_interface']
            
            # All the hostnames must be equal to cc_host (Controller host)
            # Cloud Controller host
            controller_host = parameters['cc_host']

            # Routing source IP
            routing_source_ip = parameters['routing_source_ip']
            
            # mysql database
            conn_params = self._parseConnectionString(parameters['sql_connection'])
            mysql_username = conn_params['user']
            mysql_password = conn_params['password']
            mysql_hostname = conn_params['host']
            mysql_port = conn_params['port']
            mysql_schema = conn_params['schema']

            # Authentication driver
            auth_driver = parameters['auth_driver']
    
            # libvirt virtualization type
            libvirt_type = parameters['libvirt_type']

            # log directory
            logdir = parameters['logdir']

            # state directory type
            state_path = parameters['state_path']

            # S3 Images service host
            s3_host = parameters['s3_host']

            # RabbitMQ broker host
            rabbit_host = parameters['rabbit_host']

            # EC2 API Listen port
            ec2_url = self._parseEc2Url(parameters['ec2_url'])
            ec2_url_host = ec2_url['host']
            ec2_url_port = ec2_url['port']
            ec2_url_uri = ec2_url['uri']
    
            # Force EC2 API simulation
            FAKE_subdomain = parameters['FAKE_subdomain']

            controller = self._filler.populateController(verbose, nodaemon, dhcpbridge_flagfile, dhcpbridge, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, controller_host, routing_source_ip, auth_driver, libvirt_type, logdir, state_path, s3_host, rabbit_host, ec2_url_host, ec2_url_port, ec2_url_uri, network_manager, network_fixed_range, network_size, flat_interface, FAKE_subdomain)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            controller = None
        
        return controller

# Write the parameters (if possible) from the xml file
    def write(self,xmldoc):
        controller = xmldoc
        
        verbose = self._filler.getPropertyValue(controller, 'verbose', 'enabled')
        nodaemon = self._filler.getPropertyValue(controller, 'verbose', 'enabled')

        dhcpbridge = self._filler.getPropertyValue(controller, 'dhcpbridge', 'process')
        dhcpbridge_flagfile = self._filler.getPropertyValue(controller, 'dhcpbridge', 'file')

        network_manager = self._filler.getPropertyValue(controller,'network_manager','type')
        fixed_range = self._filler.getPropertyValue(controller,'network_manager','fixed_range')
        network_size = self._filler.getPropertyValue(controller,'network_manager','network_size')
        flat_interface = self._filler.getPropertyValue(controller,'network_manager','flat_interface')

        cc_host = self._filler.getPropertyValue(controller, 'cc_host', 'hostname')
        
        routing_source_ip = self._filler.getPropertyValue(controller, 'routing_source', 'ip')

        mysql_username = self._filler.getPropertyValue(controller, 'sql_connection', 'username')
        mysql_password = self._filler.getPropertyValue(controller, 'sql_connection', 'password')
        mysql_host = self._filler.getPropertyValue(controller, 'sql_connection', 'host')
        mysql_port = self._filler.getPropertyValue(controller, 'sql_connection', 'port')
        mysql_schema = self._filler.getPropertyValue(controller, 'sql_connection', 'schema')
        sql_connection = 'mysql://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_schema

        auth_driver = self._filler.getPropertyValue(controller, 'authentication', 'driver')

        libvirt_type = self._filler.getPropertyValue(controller, 'libvirt', 'type')

        logdir = self._filler.getPropertyValue(controller, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(controller, 'state', 'path')

        s3_host = self._filler.getPropertyValue(controller, 's3_host', 'hostname')
        
        rabbit_host = self._filler.getPropertyValue(controller, 'rabbit_host', 'hostname')

        ec2url_host = self._filler.getPropertyValue(controller, 'ec2_url', 'host')
        ec2url_port = self._filler.getPropertyValue(controller, 'ec2_url', 'port')
        ec2url_uri = self._filler.getPropertyValue(controller, 'ec2_url', 'uri')
        ec2_url = 'http://' + ec2url_host + ':' + ec2url_port + ec2url_uri

        fake_subdomain = self._filler.getPropertyValue(controller, 'FAKE_subdomain', 'value')


        parameters = {'verbose':verbose, 
                      'nodaemon':nodaemon,
                      'dhcpbridge':dhcpbridge,
                      'dhcpbridge_flagfile':dhcpbridge_flagfile, 
                      'network_manager':network_manager, 
                      'fixed_range':fixed_range, 
                      'network_size':network_size,
                      'flat_interface':flat_interface,                      
                      'cc_host':cc_host, 
                      'routing_source_ip':routing_source_ip, 
                      'sql_connection':sql_connection, 
                      'auth_driver':auth_driver, 
                      'libvirt_type':libvirt_type, 
                      'logdir':logdir, 
                      'state_path':state_path,                       
                      's3_host':s3_host, 
                      'rabbit_host':rabbit_host, 
                      'ec2_url':ec2_url,
                      'FAKE_subdomain':fake_subdomain}
        
        self._writeFile(self._filename,parameters)
        return

class Configurator(object):
    '''
    classdocs
    '''
    
    _controllerConfig = ControllerConfig()
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
            
        # Add the rest of the components here...
        #
        #
        #
        
        node = self._filler.createNode(cloud)
        return node
    
    # Parse XML and extract the component configuration chosen        
    def importConfiguration(self,xml):       
        component = xml.get_cloud().get_component()[0] #ojo!
        # Is a Controller?
        if (component.get_name()=='controller'):
            controller = component
            self._controllerConfig.write(controller)
            
            # now let's start with the hard part
            utils.execute('apt-cdrom add')
            utils.execute('apt-get update')

            cmd = ['cat <<MYSQL_PRESEED | debconf-set-selections ',
               'mysql-server-5.1 mysql-server/root_password password $MYSQL_PASS ',
               'mysql-server-5.1 mysql-server/root_password_again password $MYSQL_PASS ',
               'mysql-server-5.1 mysql-server/start_on_boot boolean true ',
               'MYSQL_PRESEED']
            utils.execute( ''.join(cmd) )

            utils.execute('mount /dev/cdrom /cdrom')
            utils.execute('apt-get install -y mysql-server python-mysqldb')
    
            utils.execute("sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf")
            utils.execute('service mysql restart')
    
            utils.execute('''mysql -uroot -p$MYSQL_PASS -e "DROP DATABASE nova; CREATE DATABASE nova;"''')
            utils.execute('''mysql -uroot -p$MYSQL_PASS -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"''')
            utils.execute('''mysql -uroot -p$MYSQL_PASS -e "SET PASSWORD FOR 'root'@'%' = PASSWORD('$MYSQL_PASS');"''')

            utils.execute('mount /dev/cdrom /cdrom')
            utils.execute('apt-get install -y rabbitmq-server')

            
        # Add the rest of the components here...
        #
        #
        #
        
        return
    
        


            