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
import datetime
import inspect
from twisted.python import log
import os
import subprocess
import socket
import sys

from exception import ProcessExecutionError

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def fetchfile(url, target):
    log.msg("Fetching %s" % url)
    execute("curl --fail %s -o %s" % (url, target))

def execute(cmd, process_input=None, addl_env=None, check_exit_code=True):
    log.msg("Running cmd: %s", cmd)
    env = os.environ.copy()
    if addl_env:
        env.update(addl_env)
    obj = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    result = None
    if process_input != None:
        result = obj.communicate(process_input)
    else:
        result = obj.communicate()
    obj.stdin.close()
    (stdout,stderr) = result
    if len(stdout)>0:
        log.msg('stdout=%s' % stdout)
    if len(stderr)>0:
        log.msg('stderr=%s' % stderr)
    if obj.returncode:
        log.msg("Result was %s" % (obj.returncode))
        if check_exit_code and obj.returncode != 0:
            (stdout, stderr) = result
            raise ProcessExecutionError(exit_code=obj.returncode,
                                        stdout=stdout,
                                        stderr=stderr,
                                        cmd=cmd)
    return result

def abspath(s):
    return os.path.join(os.path.dirname(__file__), s)

def get_ip_info(interface=''):
    """Return a list with one entry for each interface.
    Entries has format: (order, name, ip_address, netmask)"""
    interfaces = []
    for line in execute('ip -f inet -o addr show %s'%(interface, ))[0].splitlines():
        line = line.split()
        order, name = line[0:2]
        ip, netmask = line[3].split('/')
        interfaces.append((int(order[:-1]), name, ip, bits2netmask(netmask)))
    return interfaces

def bits2netmask(bits):
    bits= int(bits)
    parts = []
    while bits > 0:
        if bits > 7:
            parts.append('255')
        else:
            parts.append(str((255^2**(8-bits))+1))
        bits -= 8
    if len(parts) < 4:
        parts.extend(['0']*(4-len(parts)))
    return '.'.join(parts)
