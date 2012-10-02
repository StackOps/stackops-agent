#   Copyright 2011 STACKOPS TECHNOLOGIES S.L.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Created on Sep 27, 2012

@author: German Moya
"""
import re
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import utils

from configuration import Config

class BondingConfig(Config):

    def __init__(self):
        """
        Constructor
        """

    def _configureInterfacesFile(self, bond_name, bond_slaves, bond_options):
        bond_slaves = bond_slaves.split()
        with open('/etc/network/interfaces') as f:
            interfaces = f.read()

        # Search for previous conf of any slave
        reuse_iface = None
        for slave in bond_slaves:
            if re.search( r'^[ \t]*iface[ \t]+%s' % (re.escape(slave) ), interfaces, re.M ):
                reuse_iface = slave
                break
        print 'reuse_iface', reuse_iface

        if reuse_iface:
            # Convert slave to bond
            interfaces = re.sub(
                r'(^[ \t]*iface[ \t]+)%s([ \t]+.*$)' % re.escape(reuse_iface),
                r'\1%s\2\n\t%s' % (
                    bond_name,
                    '\n\t'.join( ('bond-'+' '.join(o.split('=',1)) for o in bond_options.split()) )
                    ),
                interfaces,
                count = 1,
                flags = re.M|re.I
            )
            interfaces = re.sub(
                r'(^[ \t]*auto[ \t+](?:[^ \t]+[ \t]+)?)%s([ \t]?.*$)' % re.escape(reuse_iface),
                r'\1%s\2' % bond_name,
                interfaces,
                flags = re.M|re.I
            )
        else:
            # Create bond interface
            interfaces = '\n'.join((
                interfaces,
                'auto %s' % bond_name,
                'iface %s inet manual' % bond_name,
                '\tbond-slaves %s' % ' '.join(bond_slaves),
                '\n'.join( ('\tbond-'+' '.join(o.split('=',1)) for o in bond_options.split()) )
                ))

        # Remove previous slave conf
        for slave in bond_slaves:
            iface_match =  re.search( r'^[ \t]*iface[ \t]+%s(?:[ \t]|$)' % re.escape(slave), interfaces, re.M)
            if not iface_match:
                continue
            iface_start = iface_match.start()
            next_match = re.search( r'^[ \t]*(?:iface|mapping|auto|allow-|source)', interfaces[iface_match.end():], re.M )
            if next_match:
                iface_end = iface_start + next_match.end()
            else:
                iface_end = len(interfaces)
            interfaces = interfaces[:iface_start] + interfaces[iface_end:]
        def clean_auto(line):
            parts = line.split()
            if not parts or parts[0] != 'auto':
                return line
            parts = [p for p in parts[1:] if p not in bond_slaves]
            if not parts:
                return ''
            return 'auto %s\n' % ' '.join(parts)
        interfaces = ''.join( map(clean_auto, StringIO(interfaces)) )

        # Create slaves
        for slave in bond_slaves:
            conf = """
    auto %(slave)s
    iface %(slave)s inet manual
        bond-master %(bond)s
        bond-primary %(slaves)s
        up ifconfig $IFACE up
    """
            conf = conf % {'bond':bond_name, 'slave':slave, 'slaves': ' '.join(bond_slaves)}
            interfaces = ''.join(( interfaces, conf ))

        with open('/etc/network/interfaces', 'w') as f:
            f.write( interfaces )

    def _configureOnline(self, bond_name, bond_slaves, bond_options):
        utils.execute('modprobe bonding %s' % bond_options)
        ip_info = None
        for slave in bond_slaves:
            ip_info = utils.get_ip_info(slave)
            if ip_info:
                break
        if ip_info:
            utils.execute('ifconfig %s %s netmask %s' % (bond_name, ip_info[0][2], ip_info[0][3]))
        else:
            utils.execute('ifconfig %s up' % bond_name)
        for slave in bond_slaves.split():
            utils.execute('ifconfig %s up' % slave)
        utils.execute( 'ifenslave %s %s' % (bond_name, bond_slaves) )

    def _configureBond(self, bond_name):
        try:
            bond_slaves = getattr(self, '%s_slaves' % bond_name)
            bond_options = getattr(self, '%s_options' % bond_name)
            self._configureInterfacesFile(bond_name, bond_slaves, bond_options)
        except Exception as e:
            return 'ERROR %s' % str(e)

    def write(self, xmldoc):
        setattr(self, 'component_name', xmldoc.get_name())
        for i in xmldoc.get_service():
            service_name = i.get_type()
            for j in i.get_property():
                property_name = j.get_name()
                setattr(self, "%s_%s" % (service_name, property_name), j.get_value())
        return

    def install(self, hostname):
        try:
            self.installPackages()
            for bond_name in ('bond0', 'bond1', 'bond2'):
                if not getattr(self, '%s_slaves' % bond_name, None):
                    continue
                error =  self._configureBond(bond_name)
                if error:
                    return error
        except  Exception as inst:
            result = 'ERROR: %s' % str(inst)
        return result

    def uninstall(self, hostname):
        try:
            utils.execute('apt-get -y remove ifenslave')
        except Exception as error:
            return 'ERROR: %s' % str(error)

    def installPackages(self):
        try:
            self._installDeb('ifenslave')
        except Exception as error:
            return 'ERROR: %s' % str(error)
