"""
    Vagrant Wrapper Module

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
import subprocess

class Provider:
    """
    Exposes methods for manipulating a Vagrant based virtualized test 
    environment.
    """

    workdir="~/"
    config=None
    environment=""
 
    def __init__(self, config): 
        self.config=config
        self.helper = psupport.Helper(self.config)

    def __run_command(self,command,test_function=False):
        """
        Runs the specified command in the vagrant box. 
        Throws an error if the command returns nonzero.
	If skip_check is set, the return code is not verified. 
        """
        # We add WORKDIR functionality by wrapping each command
        # In this bash statement
        if not test_function:
            run_command = 'cd '+self.workdir+';sudo '+command

	if test_function:
   	    run_command=command 
        return sh.run(['vagrant','ssh','-c',run_command])

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
    

    def __install_kernel(self, version):
        """
        Installs the specified kernel in the vagrant box
        """
        logging.info("Rebooting Into New Kernel %s"%(version,))

        # Restart
        sh.run(['vagrant','reload'])

    def __run_dockerfile(self,verbs,arguments):
        """
        Takes each command from the Dockerfile and runs
        it in the Vagrant Box
        """
        for verb, argument in zip(verbs,arguments):
            logging.info( verb + " -> " + argument)
            if verb=="RUN":
                self.__run_command(argument)
            elif verb=="ADD":
                argument = argument.split(" ")
                self.__add(argument[0], argument[1])
            elif verb=="WORKDIR":
                self.__set_workdir(argument)
            elif verb=="KERNEL":
                self.__install_kernel(argument)
            else:
                raise exceptions.ProviderError("Command %s not recognize"%(verb,))

    def __write_vagrantfile(self, box):
        """
        Writes a custom Vagrantfile.
        Includes private networking. 
        """
        os.remove('Vagrantfile')
        f = open('Vagrantfile','w')
        data = ("Vagrant.configure(2) do |config|\n"
            '\tconfig.vm.box = "' + box + '"\n'
            '\tconfig.vm.network "private_network", type: "dhcp"\n'
            'end')
        f.write(data)       
        f.close()

    def __fetch_ip(self):
        """
        Extracts the IP address of the virtual environment. 
        """
        result = self.__run_command('ifconfig eth1')
        return re.compile('inet addr:([0-9.]+) ').search(result['stdout']).groups()[0]

    def __set_environment(self,container):
        """
        Adds test information to the bash environment of a 
        test environment by exporting them in ~/.bashrc
        """

        variables = copy.deepcopy(self.config.test_vars)
        variables['container_name'] = container
        
        command = "echo '"
        for var in variables: 
            command += 'export %s="%s"\n'%(var, variables[var])
            self.environment+='export %s="%s";'%(var,variables[var])
        command +="' >> ~/.bashrc"

        

        self.__run_command(command)

    def build_environment(self,container):
        """
        Constructs a Vagrant managed virtual machine for specified test 
        participant, based on its Dockerfile. 
        """
        
        alias = self.config.containers[container]['alias']
    
        logging.info("Building %s:%s"%(container, alias))

        [box, verbs, arguments] = self.helper.read(container, 'vagrant') 
         
        # Build Context
        os.mkdir(alias)
        os.chdir(alias)
	sh.run(['vagrant','init',box])

        # Write Custom Vagrantfile
        self.__write_vagrantfile(box)
        
        # Copy Context
        self.helper.copycontext(container)
        self.helper.copysource(container)
        self.helper.copypackages(container)
        self.helper.copytestfiles()

        # Start Box
        sh.run(['vagrant','up'])
        
        # Find IP
        ip = self.__fetch_ip()
        logging.info("IP FOUND %s"%( ip))
        self.config.containers[container]['ip']=ip

        # Follow build process with commands
        self.workdir="/"
    
        self.__run_dockerfile(verbs,arguments)    

        # Set environment
        self.__set_environment(container)

    def run_function(self,container, function):
        """
        Runs a given function in xshop_test.py inside of a specified
        participant in the test environment. Should return 
        {'ret':return_ code, 'stdout':stdout}
        """
        logging.info("Running %s in %s"%(function,container,))
	os.chdir(self.config.containers[container]['alias'])
        return sh.run(['vagrant','ssh','--',self.environment+'python2 -c "import xshop_test;import sys;sys.exit(xshop_test.%s())"'%(function,)])

    def __configure_networking(self):
        """
        Adds other container name / IP information to /etc/hosts
        """
        os.chdir(self.config.project_directory+"/"+self.config.build_directory)
        for c in self.config.compose:
            d = copy.deepcopy(self.config.compose.keys())
            alias = self.config.containers[c]['alias']
            os.chdir(alias)
            d.remove(c)
            command = "echo '"
            for e in d:
                ip = self.config.containers[e]['ip']
                command += "%s\t%s\n"%(ip, e)
            
            if 'remote:' in self.config.target:
                host = self.config.target.split(":")[1]
                command+="%s\ttarget\n"%(host,)

            command+="' | sudo tee -a /etc/hosts"
            self.__run_command(command)
            os.chdir(self.config.project_directory+"/"+self.config.build_directory)

    def attach(self, container):
        alias = self.config.containers[container]['alias']
        os.chdir(alias)
        subprocess.call(['vagrant','ssh'])                  

    def __launch_target_image(self):
        box = self.config.target.split(":")[1]
        alias = self.config.containers['target']['alias']
        os.mkdir(alias)
        os.chdir(alias)
        sh.run(['vagrant','init',box])
        self.__write_vagrantfile(box)
        self.helper.copytestfiles()
        sh.run(['vagrant','up'])
        ip = self.__fetch_ip()
        logging.info("IP FOUND %s"%( ip))
        self.config.containers['target']['ip']=ip
        self.__set_environment('target')
       

    def launch_test_environment(self):
        """
        Launches the full test environment, based on information in 
        test_environment.yml	
        """	
        logging.info("Launching environment")

        if 'image:' in self.config.target:
            self.__launch_target_image()         
   
        # Copy Test Folder to each environment
        os.chdir(self.config.project_directory+"/"+self.config.build_directory)
        for container in self.config.compose:
            alias = self.config.containers[container]['alias']
            os.chdir(alias)
            self.__add("test/*","~/")
            os.chdir('..')

        # Configure Networking
        self.__configure_networking()

        self.__set_workdir("~")   
 

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
