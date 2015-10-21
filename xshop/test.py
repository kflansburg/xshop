"""
Test Module
"""

import string
import random
import copy
import logging
import yaml
from xshop import colors
from xshop import exceptions
from xshop import template
from xshop import config
from xshop import vmanager
import shutil
import sys
import os
import traceback

class TestRunner:
    """
    Object used for executing code inside the test environment.
    """
    def __init__(self,vmanager,target):
        self.target=target
        self.vmanager = vmanager
        self.results = []
        self.vuln=False
        self.error=False

    def run(self, container, function):
        """
        Runs the specified function from xshop_test.py inside the 
        specified container and keeps the results. 
        """

        if container=='target' and ('host:' in self.target or 
            'remote:' in self.target):
            pass
        else:
            result = self.vmanager.run_function(container, function)
            self.results.append(result)
            ret = result['return_code']
            if not ret==0:
                if ret==2:
                    self.vuln=True
                else:
                    print result
                    self.error=True

class TestCase:
    """
    TestCase describes a single test, with fixed variable values.
    It exposes methods for running the test and collecting results.
    """

    def __init__(self,variables,target=""):
        """
        Initialize TestCase object with variable values and an optional
        instruction to replace the target container with either a 
        remote host or specified prebuilt container. 
        """

        self.config = config.Config(variables, target)
        self.vmanager = vmanager.VirtualizationManager(self.config)

        # Initialize Result Values
        self.vuln=None
        self.results=[]

    def __end_logging(self):
        """
        Clean up logging
        """
        for handler in self.log.handlers[:]:
            handler.close()
            self.log.removeHandler(handler)

    def __call_functions(self):
        """
        Runs xshop_test script to call functions inside test environment.
        """
        sys.path.append(self.config.project_directory+"/test")
        import xshop_test
        T = TestRunner(self.vmanager, self.config.target)
        xshop_test.run(T)
        self.results = T.results
        if T.error:
            self.test_error=True
        else:
            if T.vuln:
                self.vuln=True	
    
    def attach(self,target):
        logging.basicConfig(filename='test.log',level=logging.DEBUG)	
        self.log=logging.getLogger()
        try:
            self.vmanager.launch_test()
            self.vmanager.attach(target)
        finally:
            self.vmanager.stop_test()
            self.__end_logging()

    def run(self):
        """
        Start test environment and run test inside, returning the results"
        """
        
        logging.basicConfig(filename='test.log',level=logging.DEBUG)	
        self.log=logging.getLogger()

        self.results = []
        self.vuln = False
        self.test_error=False
        
        tb = ""
        try:
            print (colors.colors.BOLD 
                + "Running Test: " 
                + colors.colors.ENDC
                + str(self.config.variables)+", "),

            self.vmanager.launch_test()

            logging.info("Running Functions in Test Environment.")

            self.__call_functions()
    
            if self.test_error:
                raise Exception("Error Running Test")
            else:
                if self.vuln:
                    print (colors.colors.FAIL
                        + "Vulnerable"
                        + colors.colors.ENDC)
                else:
                    print (colors.colors.OKGREEN
                        + "Invulnerable"
                        + colors.colors.ENDC)

                logging.info("Result: "+str(self.vuln))

        except Exception as e:
            print colors.colors.BOLD+"ERROR!"+colors.colors.ENDC
            self.vuln = None
            tb = traceback.format_exc()
        finally:
            logging.info("Cleaning Up.")
            self.vmanager.stop_test()
            self.__end_logging()
            if not tb=="":
                print tb 
            return self.vuln

class Trial:
    """
    Manages variables in an experiment.
    """

    def __init__(self,ivars):
        """
        Accepts ivars and source and saves them as instance variables
        Recursively builds multidimensional array of test cases
        """
	self.ivars = ivars
	self.cases = self.__array_builder({},copy.deepcopy(self.ivars))	

    def __array_builder(self,d,ivars):
	"""
        Recursive function for building array of test cases.
        """
	
        # If no more variable dimensions, create test case
	if ivars=={}:
	    dnew = copy.deepcopy(d)
	    return TestCase(dnew)
	else:
	    key, value = ivars.popitem()
	    l = []
	    for v in value:
		dnew = copy.deepcopy(d)
		dnew[key]=v
		l.append(self.__array_builder(dnew,copy.deepcopy(ivars)))
	    return l

    def recursive(self,obj,func):
        """
        Recursively applies func to TestCases and returns results
        """
        if isinstance(obj,list):
            results=[]
            for o in obj:
                if isinstance(o,list):
                    results.append(self.recursive(o,func))
                else:
                    results.append(func(o))
        else:
            results = func(obj)
        return results

    # Runs a test case for each value
    def run(self):
        self.recursive(self.cases,lambda o: o.run())

    # Return results of all test cases by calling recursive function. 
    def results(self):
        return self.recursive(self.cases,
            lambda o: {
                'vuln': o.vuln,
                'vars':o.config.variables,
                'results':o.results})

    # Builds and tags images for each target container, outputs dockerfiles
    def build(self):
        if not os.path.isdir('build'):
            os.mkdir('build')
        self.recursive(self.cases,lambda o: o.build())
