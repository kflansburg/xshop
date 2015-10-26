"""
Test Module

    API for running tests in XShop
"""

import copy
import logging
from xshop import colors as clr
from xshop import exceptions
from xshop import template
from xshop import config
from xshop import vmanager
import sys
import os
import traceback

class TestCase:
    """
    TestCase describes a single test, with fixed variable values.
    It exposes methods for running the test and collecting results.
    """

    log=None
    results=[]
    vuln=None
    config=None
    vmanager=None

    def __init__(self,variables,target=""):
        """
        Initialize TestCase object with dictionary of variable values, 
        and an optional override to the target variable:
            "remote:[hostname]"
            "image:[imagename]"
        """

        self.config = config.Config(variables, target)
        self.vmanager = vmanager.VirtualizationManager(self.config)

    def __end_logging(self):
        for handler in self.log.handlers[:]:
            handler.close()
            self.log.removeHandler(handler)

    def __run_function(self, container, function):
        """
        Runs the specified function in the specified container.
        We pass this to the user in xshop_test.py.run()
        so that they may script the test procedure.  
        """

        # Dont try to run function in remote target
        if not (container=='target' and 'remote:' in self.config.target):
            result = self.vmanager.run_function(container, function)
            self.results.append(result)

            ret = result['return_code']
            if not ret==0:
                if ret==2:
                    self.vuln=True
                else:
                    print result
                    self.test_error=True

    def attach(self,target):
        """
        Starts the test environment, and attaches a shell to the 
        given container.
        """
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
            print (clr.BOLD 
                + "Running Test: " 
                + clr.ENDC
                + str(self.config.variables)+", "),

            self.vmanager.launch_test()

            logging.info("Running Functions in Test Environment.")

            sys.path.append(self.config.project_directory+"/test")
            import xshop_test
            xshop_test.run(self.__run_function)
    
            if self.test_error:
                raise Exception("Error Running Test")
            else:
                if self.vuln:
                    print (clr.FAIL
                        + "Vulnerable"
                        + clr.ENDC)
                else:
                    print (clr.OKGREEN
                        + "Invulnerable"
                        + clr.ENDC)

                logging.info("Result: "+str(self.vuln))

        except Exception as e:
            print clr.BOLD+"ERROR!"+clr.ENDC
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

    ivars={}
    cases=[]

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

    def __recursive(self,obj,func):
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

    def run(self):
        """
        Runs each TestCase and stores results.
        """
        self.__recursive(self.cases,lambda o: o.run())

    def results(self):
        """
        Returns array of test results for each variable combination. 
        Should be used after Trial.run()
        """
        return self.__recursive(self.cases,
            lambda o: {
                'vuln': o.vuln,
                'vars':o.config.variables,
                'results':o.results})
