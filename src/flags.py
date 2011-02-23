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
import os

class Flags():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def readFile(self,path,filename):
        if not os.path.exists(path + '/' + filename):
            raise Exception('File does not exists:' + path + '/' + filename)
        
        with open(path + '/' + filename,'r') as f:
            read_data = f.readlines()
            parameters = {}
            for data in read_data:
                if (data.startswith('--')):
                    parameter = data[2:].partition('=')
                    key = parameter[0].strip('\n')
                    value = ''
                    if (len(parameter[1])>0):
                        value = parameter[2].strip('\n')
#                    parameters.append({'parameter':key,'value':value})
                    parameters[key] = value
        f.closed
        return parameters
        
    def writeFile(self,path,filename,parameters):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception:
            print "Error creating directory " + path 
            raise Exception("Error creating directory " + path)
        
        try:    
            f  = open(path + '/' + filename,'w')
            f.write('# This is an automatically generated file by stackops\n')
            f.write('# Please DO NOT CHANGE the parameters manually\n')
            for parameter in iter(parameters):
                key = parameter
                value = parameters[key]
                str = key
                if (len(value)>0):
                    str = str + '=' + value
                f.write('--' + str + '\n')
            f.close()
        except Exception:
            print "Error writing file. " + path + '/' + filename
            raise Exception("Error writing file. " + path + '/' + filename)