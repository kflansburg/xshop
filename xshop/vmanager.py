"""
VirtualizationManager Module

This module interfaces TestCase instances with the user's selected
virtualization provider.
"""

from xshop import config
import importlib
from xshop import randomname
import os
import shutil
import logging

class VirtualizationManager:
    """
        VirtualizationManager Object
        
            Provides methods for manipulating the virtual test environment.
    """
    def __init__(self, config):
        # Determine Provider
        self.config = config
        self.provider_name = self.config.test_vars['provider']
    
        # Attempt to import
        try:
            self.provider = importlib.import_module(
                "xshop.providers.%s"%(self.provider_name,))
	    self.provider = self.provider.Provider(self.config)
        except ImportError as e:
            print("The provider module %s was not found"%(self.provider_name,))

    def launch_test(self):
        """
        Builds each virtual environment and starts the test environment.
        """
        # Change into new random directory
        self.config.build_directory = randomname.generate()
        os.mkdir(self.config.build_directory)        
        os.chdir(self.config.build_directory)
        logging.info("Temp Directory: %s"%(self.config.build_directory))

        # Build each environement
        for container in self.config.containers:
            if not (container=='target' and 
                ('remote:' in self.config.target or 
                'image:' in self.config.target)):
                self.provider.build_environment(container)
                os.chdir(self.config.project_directory+"/"+self.config.build_directory)
    
        # Launch test environment
        self.provider.launch_test_environment()

        os.chdir(self.config.project_directory)

    def attach(self,target):
	os.chdir(self.config.project_directory+"/"+self.config.build_directory)
	self.provider.attach(target)


    def stop_test(self):
        """
        Stops each virtual environment and cleans up temporary files.
        """
        os.chdir(self.config.project_directory+"/"+self.config.build_directory)

        # Stop test environment
        self.provider.stop_test_environment()

        # Allow provider to clean up environments
        for container in self.config.containers:
            self.provider.destroy_environment(container)
            os.chdir(self.config.project_directory+"/"+self.config.build_directory)
    
        logging.info("Removing Temp Files")
        os.chdir(self.config.project_directory)
        shutil.rmtree(self.config.build_directory)

    def run_function(self, container, function):
        """
        Runs the specified function in xshop_test.py inside of the
        virtual environment
        """
	os.chdir(self.config.project_directory+"/"+self.config.build_directory)
        return self.provider.run_function(container, function)
	os.chdir(self.config.project_directory+"/"+self.config.build_directory)
         
