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

"""
Created on Feb 21, 2011

@author: Diego Parrilla
"""
import getpass

import flags
import install
import utils
import os

class Config(object):
    '''
    classdocs
    '''

    _parameterList = set(['param1','param2','param3','param4'])
    _filename = "nofilename"

    _flags = flags.Flags()
    _filler = install.Filler()
    _operatingsystem = install.OperatingSystem()

    def __init__(self):
        """
        Constructor
        """
     
    def _readFile(self, filename):
        return self._flags.readFile("/etc/nova", filename)
        
    def _writeFile(self, filename, parameters):
        self._flags.writeFile("/etc/nova", filename, parameters)
    
    def readXML(self):
        raise NotImplementedError( "Should have implemented this" )
        
    def writeXML(self):
        raise NotImplementedError( "Should have implemented this" )
                
    def install(self,hostname):
        raise NotImplementedError( "Should have implemented this" )
    
    def checkInstallation(self):
        """
        Read the configuration file
        """
        try:
            parameters = self._readFile(self._filename)
        except Exception:
            # The file does not exists. No installation whatsoever
            return False
        
        # Exists the configuration file, but empty
        if len(self._filename)<1:
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

    def _installDeb(self,name,interactive=True):
        if (interactive):
            utils.execute('apt-get -y install %s' % name)
        else:
            utils.execute('DEBIAN_FRONTEND=noninteractive apt-get -y install %s' % name)

    def installPackagesCommon(self):
        utils.execute('apt-get -y update')
        self._installDeb('python-software-properties')
        self._installDeb('python-sqlalchemy')
        self._installDeb('python-mox')
        self._installDeb('python-greenlet')
        self._installDeb('python-carrot')
        self._installDeb('python-migrate')
        self._installDeb('python-eventlet')
        self._installDeb('python-gflags')
        self._installDeb('python-ipy')
        self._installDeb('python-tempita')
        self._installDeb('python-libxml2')
        self._installDeb('python-lxml')
        self._installDeb('python-routes')
        self._installDeb('python-cheetah')
        self._installDeb('python-netaddr')
        self._installDeb('python-paste')
        self._installDeb('python-pastedeploy')
        self._installDeb('python-mysqldb')
        self._installDeb('python-kombu')
        self._installDeb('python-novaclient')
        self._installDeb('python-xattr')
        self._installDeb('python-glance')
        self._installDeb('python-lockfile')
        self._installDeb('gawk')
        self._installDeb('curl')
        self._installDeb('socat')
        self._installDeb('unzip')
        self._installDeb('vlan')
        self._installDeb('open-iscsi')

    def installPackages(self):
        raise NotImplementedError( "Should have implemented this" )

class ControllerConfig(Config):
    '''
    classdocs
    '''

    _mysql_pass='nova'
    
    _parameterList = set(['lock_path',
                         'verbose',
                         'nodaemon',
                         'network_manager',
                         'fixed_range',
                         'network_size',
                         'sql_connection',
                         'auth_driver',
                         'logdir',
                         'state_path',
                         's3_host',
                         's3_dmz',
                         'rabbit_host',
                         'ec2_host',
                         'ec2_dmz_host',
                         'use_project_ca',
                         'flat_network_bridge',
                         'image_service',
                         'glance_api_servers',
                         'my_ip',
                         'scheduler_driver',
                         'max_cores',
                         'ec2_port',
                         's3_port'])

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

            # enable CA certs per project
            use_project_ca = parameters['use_project_ca']
                        
            controller = self._filler.populateController(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size, use_project_ca)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            controller = None
        
        return controller

# Write the parameters (if possible) from the xml file
    def write(self,xmldoc):

        iface_list = self._operatingsystem.getNetworkConfiguration()
        management_interface = self._filler.getPropertyValue(xmldoc,'interfaces','management_interface','eth0')
        my_ip='127.0.0.1'
        for iface in iface_list:
            if iface['name']==management_interface:
                my_ip = iface['address']

        verbose = self._filler.getPropertyValue(xmldoc, 'generic', 'verbose')
        nodaemon = self._filler.getPropertyValue(xmldoc, 'generic', 'nodaemon')

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
        use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca')

        logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path')

        s3_host = self._filler.getPropertyValue(xmldoc, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz')
        
        rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')

        ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')

        lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/tmp')
        
        # WARNING:THIS PARAMETERS SHOULD BE CONFIGURED FROM PROPERTY XML
        glance_hostname = self._filler.getPropertyValue(xmldoc, 'glance', 'hostname', rabbit_host) # interim solution
        glance_port = self._filler.getPropertyValue(xmldoc, 'glance', 'port', '9292')
        image_service  = self._filler.getPropertyValue(xmldoc, 'glance', 'image_service', 'nova.image.glance.GlanceImageService')
        
        max_cores = self._filler.getPropertyValue(xmldoc, 'scheduler', 'max_cores', 64)
        ec2_port = self._filler.getPropertyValue(xmldoc, 'ec2', 'port', 8773)
        s3_port = self._filler.getPropertyValue(xmldoc, 's3', 'port', 3333)
        
        scheduler_driver  = self._filler.getPropertyValue(xmldoc, 'scheduler', 'driver', 'nova.scheduler.simple.SimpleScheduler')
        flat_network_bridge = self._filler.getPropertyValue(xmldoc,'network','bridge','br100')
        
        parameters = {'lock_path':lock_path,
                      'verbose':verbose, 
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
                      'ec2_dmz_host':ec2_dmz,
                      'use_project_ca':use_project_ca,
                      'flat_network_bridge':'%s' % flat_network_bridge,
                      'image_service':'%s' % image_service,
                      'glance_api_servers':'%s:%s' % (glance_hostname,glance_port),
                      'my_ip':'%s' % my_ip,
                      'scheduler_driver': '%s' % scheduler_driver,
                      'max_cores':'%s' % max_cores,
                      'ec2_port':'%s' % ec2_port,
                      's3_port':'%s' % s3_port}
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc,hostname):
        """
        Install all stuff needed to run a controller
        """
        result =''
        try:
            if (getpass.getuser()=='root'):
                mysql_pass = self._filler.getPropertyValue(xmldoc, 'database', 'password')
                self._mysql_pass = mysql_pass
                fixed_range = self._filler.getPropertyValue(xmldoc,'network','fixed_range')
                floating_range = self._filler.getPropertyValue(xmldoc,'network','floating_range')

                # Install packages for component
                self.installPackages()
                
                utils.execute("sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf")
                utils.execute('service mysql restart')
        
                utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "DROP DATABASE nova;"''', None,None,False)
                utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "CREATE DATABASE nova;"''')
                utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"''')
                utils.execute('''mysql -uroot -p''' + mysql_pass + ''' -e "SET PASSWORD FOR 'root'@'%' = PASSWORD('nova');"''')
                
                utils.execute('killall dnsmasq',None,None,False)
                utils.execute('rm -fr /root/creds')
                utils.execute('mkdir /root/creds')
                
                # stackops
                utils.execute('adduser nova --disabled-password --gecos ""',None,None,False)

                # generate new certificates
                utils.execute('rm /var/lib/nova/nova/CA/cacert.pem /var/lib/nova/nova/CA/openssl.cnf /var/lib/nova/nova/CA/crl.pem',None,None,False)
                utils.execute('cd /var/lib/nova/nova/CA; ./genrootca.sh')
                
                # CA link to avoid issues with paths
                utils.execute('rm /var/lib/nova/CA',None,None,False)
                utils.execute('ln -s /var/lib/nova/nova/CA /var/lib/nova/CA')
    
                # nova.conf in bin linked to controller info
                utils.execute('rm /var/lib/nova/bin/nova.conf',None,None,False)
                utils.execute('ln -s /etc/nova/nova-controller.conf /var/lib/nova/bin/nova.conf')

                # create the database        
                utils.execute('/var/lib/nova/bin/nova-manage db sync')
                # create an admin user called 'admin'
                utils.execute('/var/lib/nova/bin/nova-manage user admin admin admin admin')
                # create a project called 'admin' with project manager of 'admin'
                utils.execute('/var/lib/nova/bin/nova-manage project create admin admin')
                # export credentials
                utils.execute('/var/lib/nova/bin/nova-manage project zipfile admin admin /root/creds/nova.zip')
                utils.execute('unzip /root/creds/nova.zip -d /root/creds')
                # create a small network
                utils.execute('/var/lib/nova/bin/nova-manage network create service ' + fixed_range + ' 1 255')
                # floating network
                utils.execute('/var/lib/nova/bin/nova-manage float create ' + floating_range)
                
                # enable controller components
                utils.execute('mv /etc/init/nova-ajax-console-proxy.conf.disabled /etc/init/nova-ajax-console-proxy.conf',None,None,False)
                utils.execute('mv /etc/init/nova-api.conf.disabled /etc/init/nova-api.conf',None,None,False)
                utils.execute('mv /etc/init/nova-scheduler.conf.disabled /etc/init/nova-scheduler.conf',None,None,False)
                utils.execute('mv /etc/init/nova-objectstore.conf.disabled /etc/init/nova-objectstore.conf',None,None,False)
        
                # start controller components
                utils.execute('stop nova-ajax-console-proxy; start nova-ajax-console-proxy')
                utils.execute('stop nova-api; start nova-api')
                utils.execute('stop nova-scheduler; start nova-scheduler')
                utils.execute('stop nova-objectstore; start nova-objectstore')
                utils.execute('glance-control all restart')

        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('euca2ools')
        self._installDeb('cloud-utils')
        self._installDeb('glance')
        utils.execute('echo mysql-server-5.1 mysql-server/root_password password ' + self._mysql_pass + ' | debconf-set-selections')
        utils.execute('echo mysql-server-5.1 mysql-server/root_password_again password ' + self._mysql_pass + ' | debconf-set-selections')
        utils.execute('echo mysql-server-5.1 mysql-server/start_on_boot boolean true')
        self._installDeb('mysql-server')
        self._installDeb('rabbitmq-server',False)

class ComputeConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['lock_path',
                          'network_size', 
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
                          'libvirt_type',
                          'use_project_ca',
                          'flat_interface',
                          'iscsi_ip_prefix',
                          'num_targets'])

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
            flat_interface = parameters['flat_interface']
            
            # COMPUTE-NODE SPECIFIC
            # libvirt virtualization type
            libvirt_type = parameters['libvirt_type']
    
            # enable CA certs per project
            use_project_ca = parameters['use_project_ca']

            # iscsi parameters
            iscsi_ip_prefix = parameters['iscsi_ip_prefix']
            num_targets = parameters['num_targets']

            compute = self._filler.populateCompute(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size,libvirt_type,use_project_ca,flat_interface,iscsi_ip_prefix,num_targets)
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

        flat_interface = self._filler.getPropertyValue(xmldoc,'interfaces','flat_interface')

        mysql_username = self._filler.getPropertyValue(xmldoc, 'database', 'username')
        mysql_password = self._filler.getPropertyValue(xmldoc, 'database', 'password')
        mysql_host = self._filler.getPropertyValue(xmldoc, 'database', 'host')
        mysql_port = self._filler.getPropertyValue(xmldoc, 'database', 'port')
        mysql_schema = self._filler.getPropertyValue(xmldoc, 'database', 'schema')
        sql_connection = 'mysql://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_schema

        auth_driver = self._filler.getPropertyValue(xmldoc, 'authentication', 'driver')
        use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca')

# NOVA-COMPUTE
        libvirt_type = self._filler.getPropertyValue(xmldoc, 'libvirt', 'type')

        logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path')

        s3_host = self._filler.getPropertyValue(xmldoc, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz')
        
        rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')

        ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')

        iscsi_ip_prefix = self._filler.getPropertyValue(xmldoc, 'iscsi', 'ip_prefix')
        num_targets = self._filler.getPropertyValue(xmldoc, 'iscsi', 'num_targets')

        lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/tmp')
        
        iface_list = self._operatingsystem.getNetworkConfiguration()
        management_interface = self._filler.getPropertyValue(xmldoc,'interfaces','management_interface','eth0')
        for iface in iface_list:
            if iface['name']==management_interface:
                my_ip = iface['address']
                
        parameters = {'lock_path':lock_path,
                      'verbose':verbose, 
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
                      'ec2_dmz_host':ec2_dmz,
                      'use_project_ca':use_project_ca,
                      'flat_interface':flat_interface,
                      'iscsi_ip_prefix':iscsi_ip_prefix,
                      'num_targets':num_targets}
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc,hostname):
        result=''
        try:
            flat_interface = self._filler.getPropertyValue(xmldoc,'interfaces','flat_interface')
            storage_hostname = self._filler.getPropertyValue(xmldoc, 'iscsi', 'storage_hostname')
            iscsi_ip_prefix = self._filler.getPropertyValue(xmldoc, 'iscsi', 'ip_prefix')
            ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')

            # Install packages for component
            self.installPackages()

            if (hostname!='nova-controller'):
                # enable flat interface
                utils.execute("sed -i 's/stackops.org/stackops.org\\n\\tup ifconfig " + flat_interface + " 0.0.0.0/g' /etc/network/interfaces")
                utils.execute('ifconfig ' + flat_interface + ' 0.0.0.0')
                # configure NFS mount
#                utils.execute('echo "\n' + ec2_hostname + ':/var/lib/nova/images /var/lib/nova/images nfs defaults 0 0" >> /etc/fstab')


            # add to /etc/hosts file the hostname of nova-volume
            if (storage_hostname!='nova-controller'):
                utils.execute('echo "\n' + iscsi_ip_prefix + '\t' + storage_hostname + '" >> /etc/hosts')
            
            # iptables rule to get metadata from controller
#            utils.execute('iptables -t nat -A PREROUTING -d 169.254.169.254/32 -p tcp -m tcp --dport 80 -j DNAT --to-destination ' + ec2_hostname + ':8773')             
             
            # mount NFS remote
#            utils.execute('mount -a',None,None,False)
            # enable libvirt-bin
            utils.execute('mv /etc/init/libvirt-bin.conf.disabled /etc/init/libvirt-bin.conf',None,None,False)
            # enable controller components
            utils.execute('mv /etc/init/nova-compute.conf.disabled /etc/init/nova-compute.conf',None,None,False)
            # start libvirt components
            utils.execute('stop libvirt-bin; start libvirt-bin')
            # start compute components
            utils.execute('stop nova-compute; start nova-compute')
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('kvm')
        self._installDeb('iptables')
        self._installDeb('ebtables')
        self._installDeb('user-mode-linux')
        self._installDeb('libvirt-bin')
        self._installDeb('python-libvirt')

class NetworkConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['lock_path',
                          'network_size', 
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
#                          'routing_source_ip',
                          'use_project_ca',
                          'flat_interface',
                          'public_interface'])

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
#            routing_source_ip = parameters['routing_source_ip']
            
            # Network interfaces
            public_interface = parameters['public_interface']
            flat_interface = parameters['flat_interface']

            # network configuration
            network_manager = parameters['network_manager']        
            network_fixed_range = parameters['fixed_range']
            network_size = parameters['network_size']
            
            # enable CA certs per project
            use_project_ca = parameters['use_project_ca']

#            network = self._filler.populateNetworkNode(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size,dhcpbridge_flagfile,dhcpbridge,routing_source_ip, use_project_ca,public_interface,flat_interface)
            network = self._filler.populateNetworkNode(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size,dhcpbridge_flagfile,dhcpbridge,use_project_ca,public_interface,flat_interface)
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
        routing_source_ip = self._filler.getPropertyValue(xmldoc, 'interfaces', 'routing_source_ip')
        flat_interface = self._filler.getPropertyValue(xmldoc,'interfaces','flat_interface')
        public_interface = self._filler.getPropertyValue(xmldoc,'interfaces','public_interface')

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
        use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca')
        logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path')
        s3_host = self._filler.getPropertyValue(xmldoc, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz')
        rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')
        ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')

        lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/tmp')
        
        parameters = {'lock_path':lock_path,
                      'verbose':verbose, 
                      'nodaemon':nodaemon,
# NOVA-NETWORK SPECIFIC
                      'dhcpbridge':dhcpbridge,
                      'dhcpbridge_flagfile':dhcpbridge_flagfile, 
#                      'routing_source_ip':routing_source_ip, 
                      'network_manager':network_manager, 
                      'fixed_range':fixed_range, 
                      'network_size':network_size,
                      'flat_interface':flat_interface,                      
                      'public_interface':public_interface,                      
                      'sql_connection':sql_connection, 
                      'auth_driver':auth_driver, 
                      'logdir':logdir, 
                      'state_path':state_path,                       
                      's3_host':s3_host, 
                      's3_dmz':s3_dmz, 
                      'rabbit_host':rabbit_host, 
                      'ec2_host':ec2_hostname,
                      'ec2_dmz_host':ec2_dmz,
                      'use_project_ca':use_project_ca}
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc,hostname):
        result=''
        try:
            flat_interface = self._filler.getPropertyValue(xmldoc,'interfaces','flat_interface')
            floating_range = self._filler.getPropertyValue(xmldoc,'network','floating_range')
            fixed_range = self._filler.getPropertyValue(xmldoc,'network','fixed_range')
            ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')

            # Install packages for component
            self.installPackages()

            if (hostname=='nova-controller'):
                utils.execute('echo "dummy" >> /etc/modules')
                utils.execute('modprobe dummy')
                utils.execute('ifconfig dummy0 0.0.0.0')
                
            # nova.conf in bin linked to network info
            utils.execute('rm /var/lib/nova/bin/nova.conf',None,None,False)
            utils.execute('ln -s /etc/nova/nova-network.conf /var/lib/nova/bin/nova.conf')

            # floating network
#            utils.execute('/var/lib/nova/bin/nova-manage float create ' + hostname + ' ' + floating_range)

            # enable flat interface
            utils.execute("sed -i 's/stackops.org/stackops.org\\n\\tup ifconfig " + flat_interface + " 0.0.0.0/g' /etc/network/interfaces")
            utils.execute('ifconfig ' + flat_interface + ' 0.0.0.0')

            # enable ipforwarding
#            utils.execute('echo 1 | tee /proc/sys/net/ipv4/ip_forward')
            utils.execute("sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf")
            utils.execute("sysctl -p /etc/sysctl.conf")

            # enable network components
            utils.execute('mv /etc/init/nova-network.conf.disabled /etc/init/nova-network.conf',None,None,False)
            # start network components
            utils.execute('stop nova-network; start nova-network')
#            if (hostname!='nova-controller'):
                # iptables rule to get metadata from controller
#                utils.execute('iptables -t nat -A  nova-network-POSTROUTING -s ' + fixed_range + ' -d ' + ec2_hostname + ' -j ACCEPT')             
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('dnsmasq-base')
        self._installDeb('iptables')
        self._installDeb('ebtables')

class VolumeConfig(Config):
    '''
    classdocs
    '''

    _parameterList = set(['lock_path',
                          'network_size', 
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
                          'use_project_ca',
                          'use_local_volumes'])
 
    _filename = "nova-volume.conf"

    def __init__(self):
        '''
        Constructor
        '''
# Check if there is an existing configuration file for the Controller
    def checkInstallation(self):
        check = super(VolumeConfig, self).checkInstallation()
        return check
        
# Read the parameters (if possible) and creates the config XML
    def read(self):
        volume = None
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
                
            # enable CA certs per project
            use_project_ca = parameters['use_project_ca']

            # iscsi parameters
            use_local_volumes = parameters['use_local_volumes']

            volume = self._filler.populateVolume(verbose, nodaemon, mysql_username, mysql_password, mysql_hostname, mysql_port, mysql_schema, auth_driver, logdir, state_path, s3_host, s3_dmz, rabbit_host, ec2_host, ec2_dmz_host, network_manager, network_fixed_range, network_size,use_project_ca, use_local_volumes)
        else:
            # No file or configuration, create default XML configuration
            print "No data in config file!"
            volume = None
        
        return volume

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
        use_project_ca = self._filler.getPropertyValue(xmldoc, 'authentication', 'use_project_ca')

        logdir = self._filler.getPropertyValue(xmldoc, 'logs', 'dir')
        state_path = self._filler.getPropertyValue(xmldoc, 'state', 'path')

        s3_host = self._filler.getPropertyValue(xmldoc, 's3', 'hostname')
        s3_dmz = self._filler.getPropertyValue(xmldoc, 's3', 'dmz')
        
        rabbit_host = self._filler.getPropertyValue(xmldoc, 'rabbitmq', 'hostname')

        ec2_hostname = self._filler.getPropertyValue(xmldoc, 'ec2', 'hostname')
        ec2_dmz = self._filler.getPropertyValue(xmldoc, 'ec2', 'dmz')

        use_local_volumes = self._filler.getPropertyValue(xmldoc, 'iscsi', 'use_local_volumes')

        lock_path = self._filler.getPropertyValue(xmldoc, 'generic', 'lock_path', '/tmp')
        
        parameters = {'lock_path':lock_path,
                      'verbose':verbose, 
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
                      'ec2_dmz_host':ec2_dmz,
                      'use_project_ca':use_project_ca,
                      'use_local_volumes':use_local_volumes
                      }
        
        self._writeFile(self._filename,parameters)
        return

    def install(self,xmldoc,hostname):
        result=''
        try:
            
            # Install packages for component
            self.installPackages()
            
            # LVM device to use as block storage
            lvm_device = self._filler.getPropertyValue(xmldoc,'iscsi','lvm_device')
            # enable controller components
            utils.execute('mv /etc/init/nova-volume.conf.disabled /etc/init/nova-volume.conf',None,None,False)
            # enable iscsi target
            utils.execute("sed -i 's/false/true/g' /etc/default/iscsitarget")
            utils.execute('service iscsitarget start')
            # create nova-volumes
            utils.execute('vgremove -ff nova-volumes; pvcreate -ffy ' + lvm_device)
            utils.execute('vgcreate nova-volumes ' + lvm_device)
            # start compute components
            utils.execute('stop nova-volume; start nova-volume')
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def installPackages(self):
        self.installPackagesCommon()
        self._installDeb('kpartx')
        self._installDeb('lvm2')
        self._installDeb('iscsitarget')

class Configurator(object):
    '''
    classdocs
    '''
    
    _controllerConfig = ControllerConfig()
    _computeConfig = ComputeConfig()
    _networkConfig = NetworkConfig()
    _volumeConfig = VolumeConfig()
    _filler = install.Filler();

    def __init__(self):
        '''
        Constructor
        '''

    def _changeHostname(self, hostname):
        # Change first the hostname
        utils.execute('hostname ' + hostname)
        utils.execute('echo "' + hostname + '" > /etc/hostname')
        utils.execute("sed -i 's/stackops-node/" + hostname + "/g' /etc/hosts")

    def _createCollectdConfigFile(self,configType,controllerIP):
        path = '/etc/collectd'
        filename = 'collectd.conf'
        try:
            if not os.path.exists(path):
                raise Exception("Directory " + path + " does not exists")
        except Exception:
            raise Exception("Error reading directory " + path)        
        try:    
            f  = open(path + '/' + filename,'w')
            f.write('# This is an automatically generated file by stackops\n')
            f.write('# Change the parameters manually at your own risk\n')
            f.write('FQDNLookup true\n')
            f.write('\n')            
            f.write('LoadPlugin "logfile"\n')
            f.write('LoadPlugin "network"\n')
            f.write('\n')
            if configType & 1 == 1 :
                f.write('# Server configuration\n')    
                f.write('LoadPlugin "rrdtool"\n')
                f.write('\n')

            f.write('# Client configuration\n')
            f.write('LoadPlugin "interface"\n')
            f.write('LoadPlugin "cpu"\n')
            f.write('LoadPlugin "memory"\n')
            f.write('LoadPlugin "df"\n')
            f.write('LoadPlugin "disk"\n')
            f.write('LoadPlugin "vmem"\n')
            f.write('LoadPlugin "swap"\n')
            if (configType & 8 == 8):
                f.write('# compute node specific\n')    
                f.write('LoadPlugin "libvirt"\n')
            if (configType & 2 == 2):
                f.write('# network node specific\n')    
                f.write('LoadPlugin "iptables"\n')

            f.write('\n')
            f.write('<Plugin "network">\n')
            if configType & 1 == 1 :
                f.write('  Listen "' + controllerIP + '"\n')
            f.write('  Server "' + controllerIP + '"\n')
            f.write('</Plugin>\n')
            f.write('\n')

            if configType & 1 == 1 :
                f.write('<Plugin rrdtool>\n')
                f.write('  DataDir "/var/lib/collectd/rrd"\n')
                f.write('</Plugin>\n')
                f.write('\n')
            
            f.write('<Plugin "interface">\n')
            f.write('  Interface "lo"\n')
            f.write('  IgnoreSelected true\n')
            f.write('</Plugin>\n')

            if (configType == 8) or (configType == 15):
                f.write('<Plugin "libvirt">\n')
                f.write('  Connection "qemu:///system"\n')
                f.write('  HostnameFormat "name"\n')
                f.write('</Plugin>\n')
            
            f.close()
        except Exception:
            print "Error writing file. " + path + '/' + filename
            raise Exception("Error writing file. " + path + '/' + filename)        



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

        # Is a Volume?
        if (self._volumeConfig.checkInstallation()):
            volume = self._volumeConfig.read()
            cloud = self._filler.populateCloud(cloud, volume, None)
        # Add the rest of the components here...
        #
        #
        #
        
        node = self._filler.createNode(cloud)
        return node

    def importConfiguration(self,xml):
        """
        Import the configuration from the XML definition file, and configure the selected nodes.
        You must be root to execute this method
        """
        if getpass.getuser()=='root':
            # Change hostname from XML information
            hostname = xml.get_software().get_os().get_network().get_hostname()
            # Change hostname
            self._changeHostname(hostname)
            configType = 0
            for component in xml.get_cloud().get_component():
                collectd_listener = self._filler.getPropertyValue(component, 'monitoring', 'collectd_listener','localhost')
                # Is a Controller?
                if component.get_name()=='controller':
                    configType |= 1
                    self._controllerConfig.write(component)
                    result = self._controllerConfig.install(component,hostname)
                    if len(result)>0:
                        return result
                # Is a Compute?
                if component.get_name()=='compute':
                    configType |= 8
                    self._computeConfig.write(component)
                    result = self._computeConfig.install(component,hostname)
                    if len(result)>0:
                        return result
                # Is a Network?
                if component.get_name()=='network':
                    configType |= 2
                    self._networkConfig.write(component)
                    result = self._networkConfig.install(component,hostname)
                    if len(result)>0:
                        return result
                # Is a Volume?
                if component.get_name()=='volume':
                    configType |= 4
                    self._volumeConfig.write(component)
                    result = self._volumeConfig.install(component,hostname)
                    if len(result)>0:
                        return result
            # Add the rest of the components here...
            #
            #
            #
            # configType = 15, single node
            # configType = 7, dual node controller
            # configType = 1, 2, 4 multinode
            # configType = 8 dual o multinode (compute node)
        
            # Deprecated.
            #        self._createCollectdConfigFile(configType,collectd_listener)
            #        utils.execute('service collectd restart')
            return ''
        else:
            return 'You should run this program as super user.'
    
        


            
