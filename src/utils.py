'''
Created on 16/11/2010

@author: diego
'''

import datetime
import inspect
import logging
import os
import subprocess
import socket
import sys

from exception import ProcessExecutionError

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def fetchfile(url, target):
    logging.debug("Fetching %s" % url)
    execute("curl --fail %s -o %s" % (url, target))

def execute(cmd, process_input=None, addl_env=None, check_exit_code=True):
    logging.debug("Running cmd: %s", cmd)
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
    print stdout
    print stderr 
    if obj.returncode:
        logging.debug("Result was %s" % (obj.returncode))
        if check_exit_code and obj.returncode != 0:
            (stdout, stderr) = result
            raise ProcessExecutionError(exit_code=obj.returncode,
                                        stdout=stdout,
                                        stderr=stderr,
                                        cmd=cmd)
    return result


def abspath(s):
    return os.path.join(os.path.dirname(__file__), s)
