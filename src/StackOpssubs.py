#!/usr/bin/env python

#
# Generated Tue Jan 25 13:17:30 2011 by generateDS.py version 2.3b.
#

import sys

import StackOps as supermod

etree_ = None
Verbose_import_ = False
(   XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class nodeSub(supermod.node):
    def __init__(self, hardware=None, software=None, cloud=None):
        super(nodeSub, self).__init__(hardware, software, cloud, )
supermod.node.subclass = nodeSub
# end class nodeSub


class hardwareSub(supermod.hardware):
    def __init__(self, cpus=None, virtualization=None, memory=None, nics=None, partitions=None):
        super(hardwareSub, self).__init__(cpus, virtualization, memory, nics, partitions, )
supermod.hardware.subclass = hardwareSub
# end class hardwareSub


class cpusSub(supermod.cpus):
    def __init__(self, cpu=None):
        super(cpusSub, self).__init__(cpu, )
supermod.cpus.subclass = cpusSub
# end class cpusSub


class cpuSub(supermod.cpu):
    def __init__(self, cores=None, speed=None, name=None, valueOf_=None):
        super(cpuSub, self).__init__(cores, speed, name, valueOf_, )
supermod.cpu.subclass = cpuSub
# end class cpuSub


class nicsSub(supermod.nics):
    def __init__(self, nic=None):
        super(nicsSub, self).__init__(nic, )
supermod.nics.subclass = nicsSub
# end class nicsSub


class nicSub(supermod.nic):
    def __init__(self, interface=None, type_=None, name=None, valueOf_=None):
        super(nicSub, self).__init__(interface, type_, name, valueOf_, )
supermod.nic.subclass = nicSub
# end class nicSub


class partitionsSub(supermod.partitions):
    def __init__(self, partition=None):
        super(partitionsSub, self).__init__(partition, )
supermod.partitions.subclass = partitionsSub
# end class partitionsSub


class partitionSub(supermod.partition):
    def __init__(self, device=None, mountpoint=None, used=None, size=None, valueOf_=None):
        super(partitionSub, self).__init__(device, mountpoint, used, size, valueOf_, )
supermod.partition.subclass = partitionSub
# end class partitionSub


class softwareSub(supermod.software):
    def __init__(self, os=None):
        super(softwareSub, self).__init__(os, )
supermod.software.subclass = softwareSub
# end class softwareSub


class osSub(supermod.os):
    def __init__(self, uname=None, network=None):
        super(osSub, self).__init__(uname, network, )
supermod.os.subclass = osSub
# end class osSub


class networkSub(supermod.network):
    def __init__(self, hostname=None, nameserver=None, iface=None):
        super(networkSub, self).__init__(hostname, nameserver, iface, )
supermod.network.subclass = networkSub
# end class networkSub


class ifaceSub(supermod.iface):
    def __init__(self, name=None, default=None, virtual=None, netmask=None, address=None, dhcp=None, gateway=None, valueOf_=None):
        super(ifaceSub, self).__init__(name, default, virtual, netmask, address, dhcp, gateway, valueOf_, )
supermod.iface.subclass = ifaceSub
# end class ifaceSub


class cloudSub(supermod.cloud):
    def __init__(self, topology=None, component=None):
        super(cloudSub, self).__init__(topology, component, )
supermod.cloud.subclass = cloudSub
# end class cloudSub


class topologySub(supermod.topology):
    def __init__(self, management=None, storage=None, service=None, valueOf_=None):
        super(topologySub, self).__init__(management, storage, service, valueOf_, )
supermod.topology.subclass = topologySub
# end class topologySub


class componentSub(supermod.component):
    def __init__(self, name=None, service=None):
        super(componentSub, self).__init__(name, service, )
supermod.component.subclass = componentSub
# end class componentSub


class serviceSub(supermod.service):
    def __init__(self, type_=None, property=None):
        super(serviceSub, self).__init__(type_, property, )
supermod.service.subclass = serviceSub
# end class serviceSub


class propertySub(supermod.property):
    def __init__(self, name=None, value=None, valueOf_=None):
        super(propertySub, self).__init__(name, value, valueOf_, )
supermod.property.subclass = propertySub
# end class propertySub



def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    if hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'node'
        rootClass = supermod.node
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'node'
        rootClass = supermod.node
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'node'
        rootClass = supermod.node
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from ??? import *\n\n')
    sys.stdout.write('import ??? as model_\n\n')
    sys.stdout.write('rootObj = model_.node(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="node")
    sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()


