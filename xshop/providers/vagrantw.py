"""
    Vagrant Wrapper Module

        Exposes methods for constructing test environments with Vagrant
"""

from xshop import template
from xshop import xshopfile
from xshop import exceptions
from xshop import sh
from xshop import colors
import os
import logging


class Provider:
    """
    Exposes methods for manipulating a Vagrant based virtualized test 
    environment.
    """

    workdir="~/"
    config=None
 
    def __init__(self, config): 
        self.config=config

    def __run_command(self,command,test_function=False):
        """
        Runs the specified command in the vagrant box. 
        Throws an error if the command returns nonzero.
	If skip_check is set, the return code is not verified. 
        """
        # We add WORKDIR functionality by wrapping each command
        # In this bash statement
        run_command = '/bin/bash -c "cd '+self.workdir+';sudo %s"'%(command,)

	if test_function:
   	    run_command=command 
        result = sh.run(['vagrant','ssh','-c', run_command])
        if result['return_code'] and not test_function:
            raise ProviderError("Command '%s' returned %d\n%s\n%s"%(
		command,
		result['return_code'],
		result['stdout'],
		result['stderr'] ))

	return result

    def __set_workdir(self,workdir):
        """
        Sets the WORKDIR variable so that all subsequent commands will
        be run from that directory
        """
        self.workdir=workdir

    def __add(self,infile, outfile):
        """
        All files in context are included at /vagrant
        This method copies from there to the specified location
        To mimic Docker's idiocy, we have to automatically untar
        any archives.
        """    
        extensions = (".tar.gz",".tar.bz2",".tar.xz",".tar")
        infile = str(infile)
        if infile.endswith(extensions):
            sh.run(['tar','-xf',infile])
            for e in extensions:
                infile = infile.replace(e,"")

        self.__run_command("cp -r /vagrant/%s %s"%(infile, outfile))
    

    def __install_kernel(self,):
        """
        Installs the specified kernel in the vagrant box
        """
        # Download packages
    
        # Dpkg
    
        # Restart
        pass

    def __run_dockerfile(self,verbs,arguments):
        """
        Takes each command from the Dockerfile and runs
        it in the Vagrant Box
        """
        for verb, argument in zip(verbs,arguments):
            print verb + " -> " + argument
            if verb=="RUN":
                self.__run_command(argument)
            elif verb=="ADD":
                argument = argument.split(" ")
                self.__add(argument[0], argument[1])
            elif verb=="WORKDIR":
                self.__set_workdir(argument)
            else:
                raise exceptions.ProviderError("Command %s not recognize"%(verb,))

    def __determine_source_box(self,verbs,arguments):
        box = None
        if 'FROM' in verbs:
            box = arguments[verbs.index('FROM')]
        if 'VAGRANT_FROM' in verbs:
            box = arguments[verbs.index('VAGRANT_FROM')]
        if box==None:
            raise exceptions.ProviderError("No FROM statement found. "
                "Cannot determine source box.")
    
        # Remove any FROM commands
        return ([list(t) for t in zip(*filter(lambda v: not "FROM" in v[0], 
                zip(verbs,arguments)))], box)
        

    def build_environment(self,container):
        """
        Constructs a Vagrant managed virtual machine for specified test 
        participant, based on its Dockerfile. 
        """
        
        alias = self.config.containers[container]['alias']
    
        logging.info("Building %s:%s"%(container, alias))

        [verbs,arguments] = xshopfile.read(self.config,container) 
  
        ([verbs,arguments],box) = self.__determine_source_box(verbs,arguments) 
         
        # Build Context
        os.mkdir(alias)
        os.chdir(alias)
	sh.run(['vagrant','init',box])

        # Copy Context
        context = self.config.containers[container]['build_files_directory']
        sh.run('cp %s/* .'%(context,),shell=True)

        # Copy Source
        if self.config.test_vars['install_type']=='source':
            sh.run(['cp',self.config.source_path,'.'])

        # Copy Test
        sh.run(['cp','-r',self.config.test_directory,"."])

        # Start Box
        sh.run(['vagrant','up'])
    
        # Follow build process with commands
        self.workdir="/"
    
        self.__run_dockerfile(verbs,arguments)    


    def run_function(self,container, function):
        """
        Runs a given function in xshop_test.py inside of a specified
        participant in the test environment. Should return 
        {'ret':return_ code, 'stdout':stdout}
        """
        print "Running %s in %s"%(function,container,)
	os.chdir(self.config.containers[container]['alias'])
        command = 'python2 -c "import xshop_test;import sys;sys.exit(xshop_test.%s())"'%(function,)
	return self.__run_command(command, test_function=True)

    def launch_test_environment(self):
        """
        Launches the full test environment, based on information in 
        test_environment.yml	
        """	
        logging.info("Launching environment")
        # Configure Networking

    def stop_test_environment(self):
        """ 
        Stops virtual test environment
        """
        # Vagrant can simply call destroy later
        pass

    def destroy_environment(self,container):
        """
        Removes virtual environment
        """
        alias = self.config.containers[container]['alias']

        if os.path.isdir(alias):
            os.chdir(alias)
            sh.run(['vagrant','destroy','-f'])
