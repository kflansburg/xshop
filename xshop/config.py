#
#	config
#
#		Module that persists project information in
#		a file named .config in the root of the 
#		project directory
#

import copy
import os
import yaml
from xshop import exceptions
from xshop import randomname

def generate_new_config(library):
    """
    Generates an empty configuration file
    """

    config = {
        "constants":{
            "build_dependencies": [],
            "library":library,
            "install_type":"source",
            "provider":"docker"},
        "variables":{"version":[]},
        "source":[],
        "public_keys":[],
        "notes":""
    }

    f = open('config.yml','w')
    f.write(yaml.dump(config))
    f.close()

def variables():
    """
    Reads just the variables from the config file.
    """
    if not os.path.isfile('config.yml'):
        raise exceptions.ConfigError("No configuration file found.")
    
    f = open('config.yml','r')
    config = yaml.load(f.read())
    if not 'variables' in config:
        raise exceptions.ConfigError("No variables in configuration.")
    return config['variables']

class Config:
    """
    Object for collecting information specific to a project and test case.
    """

    project_directory=None
    build_directory=None  
    source_directory=None
    test_directory=None
 
    config={}

    test_vars={}

    variables={}

    compose={}
    containers={}

    target=None

    def __init__(self, variables, target):

        self.project_directory = os.getcwd()
	self.test_directory = self.project_directory+"/test"

        self.variables = variables
    
        self.target=target

        self.config = self.__load_file('config.yml')

        self.__verify_parse_config()

        self.compose = self.__load_file('docker-compose.yml')
        
        self.__randomize_container_names()
         
    def __load_file(self, filename):
        full_file_path = self.project_directory+"/"+filename
        if os.path.isfile(full_file_path):
            f = open(full_file_path)
            return yaml.load(f.read())
        else:
            raise exceptions.ConfigError("%s not found"%(filename,))

    def __randomize_container_names(self):
        self.containers={}
        for c in self.compose:
            build_files_directory = self.project_directory+"/containers/"+c
            self.containers[c] = {'alias':randomname.generate(),
                'build_files_directory':build_files_directory}
        
        if "remote:" in self.target:
            self.compose.pop('target')

    def __verify_parse_config(self):
        ## Optional Stuff
        if not 'constants' in self.config:
            self.config['constants'] = {}
       
        self.test_vars = copy.deepcopy(self.config['constants'])
        self.test_vars.update(self.variables)
    
        ## Required Stuff
        if not 'provider' in self.test_vars:
            raise exceptions.ConfigError("No provider found!")

        if not 'install_type' in self.test_vars:
            raise exceptions.ConfigError("No install type found!")

        if self.test_vars['install_type']=='source' and self.target=="":
            if not 'version' in self.test_vars:
                raise exceptions.ConfigError("No version for source")
            if not 'library' in self.test_vars:
                raise exceptions.ConfigError("No library found for source")
            self.source_path = (self.project_directory + 
                "/source/%s-%s.tar.gz")%(self.test_vars['library'],
                    self.test_vars['version'],)

