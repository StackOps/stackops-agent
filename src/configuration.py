import sys

import flags
import install
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

    _parameterList = set(['sql_connection', 's3_host', 'rabbit_host', 'cc_host', 'verbose', 'ec2_url', 'network_manager', 'fixed_range', 'network_size'])
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
            conn_params = self._parseConnectionString(parameters['sql_connection'])
            ec2_url = self._parseEc2Url(parameters['ec2_url'])
            
            mysql_username = conn_params['user']
            mysql_password = conn_params['password']
            mysql_hostname = conn_params['host']
            mysql_port = conn_params['port']
            mysql_schema = conn_params['schema']
    
            # All the hostnames must be equal to cc_host (Controller host)
            cc_host = parameters['cc_host']
            s3_host = parameters['s3_host']
            rabbit_host = parameters['rabbit_host']
            ec2_host = ec2_url['host']

            verbose = parameters['verbose']
            ec2_url_port = ec2_url['port']
            ec2_url_uri = ec2_url['uri']
            network_manager = parameters['network_manager']        
            fixed_range = parameters['fixed_range']
            network_size = parameters['network_size']
    
            controller = self._filler.populateController(mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, cc_host, ec2_url_port, ec2_url_uri, network_manager, fixed_range, network_size)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            controller = None
        
        return controller

# Write the parameters (if possible) from the xml file
    def write(self,xmldoc):
        controller = xmldoc
        
        mysql_username = self._filler.getPropertyValue(controller, 'sql_connection', 'username')
        mysql_password = self._filler.getPropertyValue(controller, 'sql_connection', 'password')
        mysql_host = self._filler.getPropertyValue(controller, 'sql_connection', 'host')
        mysql_port = self._filler.getPropertyValue(controller, 'sql_connection', 'port')
        mysql_schema = self._filler.getPropertyValue(controller, 'sql_connection', 'schema')
        sql_connection = 'mysql://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_schema

        s3_host = self._filler.getPropertyValue(controller, 's3_host', 'hostname')
        rabbit_host = self._filler.getPropertyValue(controller, 'rabbit_host', 'hostname')
        cc_host = self._filler.getPropertyValue(controller, 'cc_host', 'hostname')
        verbose = self._filler.getPropertyValue(controller, 'verbose', 'enabled')

        ec2url_host = self._filler.getPropertyValue(controller, 'ec2_url', 'host')
        ec2url_port = self._filler.getPropertyValue(controller, 'ec2_url', 'port')
        ec2url_uri = self._filler.getPropertyValue(controller, 'ec2_url', 'uri')
        ec2_url = 'http://' + ec2url_host + ':' + ec2url_port + ec2url_uri

        network_manager = self._filler.getPropertyValue(controller,'network_manager','type')
        fixed_range = self._filler.getPropertyValue(controller,'network_manager','fixed_range')
        network_size = self._filler.getPropertyValue(controller,'network_manager','network_size')

        parameters = {'sql_connection':sql_connection, 's3_host':s3_host, 
                      'rabbit_host':rabbit_host, 'cc_host':cc_host, 
                      'verbose':verbose, 'ec2_url':ec2_url, 
                      'network_manager':network_manager, 'fixed_range':fixed_range, 
                      'network_size':network_size}
        
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
            
        # Add the rest of the components here...
        #
        #
        #
        
        return
    
        


            