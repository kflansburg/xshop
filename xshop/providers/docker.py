"""
Docker Wrapper Module

Exposes methods for constructing test environments with Vagrant
"""

from xshop import template
from xshop import psupport
from xshop import exceptions
from xshop import sh
import os
import logging
import re
import copy
import yaml
import subprocess

class Provider:
    """
    Exposes methods for manipulating a Docker based virtualized test 
    environment.
    """

    config=None
    helper=None
 
    def __init__(self, config): 
        
        self.config=config
        self.helper=psupport.Helper(self.config)

    def build_environment(self,container):
        """
        Builds a Docker image for the specified container.
        """
        
        alias = self.config.containers[container]['alias']
        
        os.mkdir(alias)
        os.chdir(alias)

        # Copy Context Files
        self.helper.copycontext(container)
        self.helper.copysource(container)
        self.helper.copypackages(container)

        # Get Dockerfile
        [baseimage,verbs,arguments] = self.helper.read(
            container,
            'docker')

        # Write Dockerfile
        f = open('Dockerfile','w')
        f.write('FROM %s\n'%(baseimage,))        
        for verb,argument in zip(verbs,arguments):
            f.write('%s %s\n'%(verb,argument,))
        f.close()

        # Build
        sh.run(['docker','build','-t',alias, '.'])

    def run_function(self,container, function):
        """
        Runs a given function in xshop_test.py inside of a specified
        participant in the test environment.
        """
        alias = self.config.containers[container]['alias']
    
        return sh.run(['docker',
            'exec',
            "xshop_"+alias+"_1",
            'python2',
            '-c',
            "import xshop_test;import sys;sys.exit(xshop_test." 
            + function
            + "())"])

    def __create_compose_context(self,container):
        """
        Creates a build context for the specified container
        for use with Docker Compose.
        """
        alias = self.config.containers[container]['alias']
        if container=='target' and 'image:' in self.config.target:
            image = ':'.join(self.config.target.split(":")[1:])
            alias = image

        os.mkdir(container)
        os.chdir(container) 
   
        # Copy in Test
        self.helper.copytestfiles()

        # Write out Dockerfile
        f = open('Dockerfile','w')
        f.write("FROM %s\n"%(alias))
        f.write("ADD test ~/\n")
        f.write("WORKDIR ~")
        f.close()

    def __create_compose_file(self):
        """
        Generates a modified Compose file.
        Replaces container names with aliases. 
        Replaces links with aliases. 
        Introduces required environment variables. 
        """

        compose = copy.deepcopy(self.config.compose)
        new_compose = {}    
        for container in compose:

            # Update Links to Alias            
            if 'links' in compose[container]:
                newlinks = []
                for l in compose[container]['links']:
                    if not (l=='target' and 'remote:' in self.config.target):
                        newlinks.append("%s:%s"%(self.config.containers[l]['alias'],l,))

                compose[container]['links'] = newlinks
        
                
            # Set Environment
            compose[container]['environment']={}
            for k,v in self.config.test_vars.iteritems():
                compose[container]['environment'][k]=v
            compose[container]['environment']['container_name'] = container

            # Support Attacking Remove
            if 'remote:' in self.config.target:
                host = self.config.target.split(":")[1]
                compose[container]['extra_hosts'] = ["target:"+host]

            alias = self.config.containers[container]['alias']
            new_compose[alias] = compose[container]

        f = open('docker-compose.yml','w')
        f.write(yaml.dump(new_compose))
        f.close()

    def launch_test_environment(self):
        """
        Launches the full test environment, based on information in 
        test_environment.yml	
        """
        # Create Compose Context
        compose_directory = (self.config.project_directory
            + "/"
            + self.config.build_directory
            + "/compose")

        os.mkdir(compose_directory)
        os.chdir(compose_directory)
        
        for container in self.config.containers:
            self.__create_compose_context(container)
            os.chdir(compose_directory)
       
        self.__create_compose_file()

        # Launch
        sh.run(['docker-compose','-p','xshop','build'])
        sh.run(['docker-compose','-p','xshop','up','-d'])	

    def stop_test_environment(self):
        """ 
        Stops virtual test environment
        """
        pass

    def attach(self,target):
        """
        Spawn an interactive shell in the specified container.
        """
        alias = self.config.containers[target]['alias']
        subprocess.call(['docker','exec','-i','-t','xshop_%s_1'%(alias), '/bin/bash'])

    def destroy_environment(self,container):
        """
        Removes virtual environment
        """
        for container in self.config.containers:
            alias = self.config.containers[container]['alias']
            sh.run(['docker','kill','xshop_%s_1'%(alias)])
            sh.run(['docker','rm','xshop_%s_1'%(alias)])
