#
#	Test
#
#		This module defines 3 classes:
#
#		TestCase(dict_of_var_vals,{source|debian|remote}) 
#			- Models a single test with fixed variables
#
#			TestCase.run() - Runs test and returns true/false
#
#		Trial({var1:[vals],...},{source|debian|remote})
#			- Describes independent variables for testing and 
#			manages multiple TestCases
#
#			Trial.run() - Runs all tests
#
#			Trial.results() - Returns multidimensional array of test results
#
#		HookRunner([]* results)
#			- Passed to user for running hooks in test environment, 
#				collects results to be returned to xshop
#

import string
import random
import copy
import logging
import yaml
from xshop import colors
from xshop import exceptions
from xshop import template
from xshop import dockerw
from xshop import config
import shutil
import sys
import os

# Returns a random 10 character uppercase string for naming
# containers
def random_name():
	return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

TMP_FOLDER='test-tmp'

class HookRunner:
	def __init__(self,results,containers,target):
                self.target=target
		self.error=False
		self.vuln=False
		self.results = results
		self.containers = containers
	def run(self,container,hook):
                if container=='target' and (not (self.target==None or self.target=='host')):
                    # Skip hook, remote target
                    pass
                else:
                        result = dockerw.run_hook(self.containers[container],hook)
                        self.results.append(result)
                        ret = result['ret']
                        if not ret==0:
                                if ret==2:
                                        self.vuln=True
                                else:
                                        self.error=True

class TestCase:
	def __init__(self,variables,target=None):
		# Get Project Configuration
                self.config = config.Config()
		self.proj_dir = os.getcwd()
                self.compose = config.parse_docker_compose()
                self.library=self.config.get('library')
		self.variables = variables
                self.target = target
                try:
                    self.constants = self.config.get('constants')
                except KeyError:
                    self.constants = {}

		# Build Dictionary of Containers and Their Random Names
		self.containers = {}
		for c in self.compose:
			self.containers[c]=random_name()
		
                self.install_type = self.config.get('install_type')
                
                if 'version' in self.variables:
                    self.version = self.variables['version']
                elif 'version' in self.constants:
                    self.version = self.constants['version']
                else:
                    self.verions = ''

		# Initialize Result Values
		self.vuln=None
		self.results=[]

	# Builds template dict by adding non independent variables
	def __templated(self,name):
		templated = copy.deepcopy(self.variables)
                templated.update(self.constants)
		templated['container_name'] = name
		templated['library'] = self.library
                templated['install_type'] = self.install_type
		return templated	

	# Returns the dockerfile of a given container
	def dockerfile(self,name):
		templated = self.__templated('target')
		return template.template_file_contents('containers/%s/Dockerfile'%(name,),
			templated)

	# Builds the dockerfile of a container, tagging it as 
	# xshop:[container]_build
	def __build_container(self,name, image_name):
		global TMP_FOLDER
		TMP_FOLDER = random_name()

		if name=='target' and self.target=='host':
			# Build Host Image
			if not dockerw.image_exists('xshop:host'):
				raise exceptions.DockerError('Please use `xshop build_image host` to construct an image of the host machine. This should be done any time changes are made to the host system.')



		elif name=='target' and (not self.target==None):
			pass
			# Dont build target, attacking remote

		else:
			# Construct image for container from supplied context	
			templated = self.__templated(name)	

			# Create temporary build context
			template.copy_and_template("containers/%s"%(name,), 
				TMP_FOLDER,
				templated)

			# Copy in any necessary files
			if name=='target':
				if self.install_type=='source':
					source_file = "%s/source/%s-%s.tar.gz"%\
						(self.proj_dir, self.library, self.version)
					shutil.copy2(source_file, TMP_FOLDER+"/")
				elif self.install_type=='debian':
					pkg_dir = "%s/packages/%s-%s/"%\
						(self.proj_dir, self.library, self.version)
					shutil.copytree(pkg_dir, 
						TMP_FOLDER+"/%s-%s"%\
						(self.library, self.self.version,))

		
			dockerw.run_docker_command(['docker','build','-t',image_name,TMP_FOLDER])
			shutil.rmtree(TMP_FOLDER)
		

	# Builds each container from supplied Dockerfile	
	def __build_containers(self):
		for c,v in self.containers.iteritems():
			logging.info(colors.colors.OKGREEN\
				+"Building %s"%(c,)\
				+colors.colors.ENDC)
			self.__build_container(c,"xshop:%s_build"%(v,))
			logging.info(colors.colors.OKGREEN\
				+"Done."\
				+colors.colors.ENDC)

	# Creates temporary context to launch experiment with docker compose
	def __create_compose_context(self):
		global TMP_FOLDER
		TMP_FOLDER=random_name()

		os.mkdir(TMP_FOLDER)
		os.mkdir(TMP_FOLDER+"/containers")
		# For each container
		for c,v in self.containers.iteritems():
                        # Skip building remote target
                        if c=='target' and (not (self.target==None or self.target=='host')):
                                pass    
                        else:                                
                                # Create Context Folder
                                os.mkdir(TMP_FOLDER+"/containers/"+c)
                                # Copy in test code
                                shutil.copytree(self.proj_dir+'/test',
                                        TMP_FOLDER+"/containers/"+c+"/test")
                                # Write out Dockerfile
                                f=open(TMP_FOLDER+"/containers/"+c+"/Dockerfile",'w')

                                if c=='target' and self.target=='host':
                                        # FROM xshop:host
                                        dockerfile="FROM xshop:host\n"
                                else:
                                        dockerfile="FROM xshop:%s_build\n"%(v,)


                                dockerfile+="ADD test /home/\n"\
                                                        "WORKDIR /home/\n"

                                f.write(dockerfile)
                                f.close()

		# Copy in compose, substituting container pseudonyms
		f = open(self.proj_dir+"/docker-compose.yml",'r')
		d = yaml.load(f.read())
		f.close()
		
		newd={}	
	
		for c in d:
                        if c=='target' and (not (self.target==None or self.target=='host')):
                                # Dont include remote target in docker compose file
                                pass
                        else:
                                newc = self.containers[c]

                                # Update links to match random names
                                if 'links' in d[c].keys():
                                        newlinks=[]
                                        for l in d[c]['links']:
                                                # Only add target link for non remote attack
                                                if l=='target' and (not (self.target==None or self.target=='host')):
                                                        pass
                                                else:
                                                        newlinks.append("%s:%s"%(self.containers[l],l,))
                            
                                        d[c]['links']=newlinks
                                
                                # For remote attack, add outgoing route
                                if not (self.target==None or self.target=='host'):
                                        d[c]['extra_hosts']=['target:'+self.target]
                      

                                if not 'environment' in d[c].keys():
                                        d[c]['environment']={}                        
                                for key in self.constants:
                                        val = self.constants[key]
                                        if val and not val=='':
                                                d[c]['environment'][key]=val
                                for key in self.variables:
                                        val = self.variables[key]
                                        if val and not val=='':
                                                d[c]['environment'][key]=val

                                d[c]['environment']['container']=c
                                newd[newc]=d[c]

		f = open(TMP_FOLDER+'/docker-compose.yml','w')
                print newd
		f.write(yaml.dump(newd))
		f.close()


	# Cleans up logging
	def __end_logging(self):
		for handler in self.log.handlers[:]:
			handler.close()
			self.log.removeHandler(handler)

	def export(self):
                # Generates Dockerfile for TestCase
		name = '_'.join(map(lambda x: self.variables[x],sorted(self.variables.keys())))
		
                f = open(self.proj_dir+'/build/Dockerfile_'+name,'w')
		f.write(self.dockerfile('target'))
	        f.close()

	# Removes temporary test resources
	def __clean_test(self):
		# Terminate Test Containers
		dockerw.compose_down()

		# Remove temporary compose folder
		os.chdir(self.proj_dir)
		if os.path.isdir(TMP_FOLDER):
			shutil.rmtree(TMP_FOLDER)	
	
		

	# Call exploit hook in each container and stores results	
	def __call_hooks(self):
		sys.path.append(self.proj_dir+"/test")
		import xshop_test
		H = HookRunner(self.results,self.containers,self.target)
		xshop_test.run(H)
		if H.error:
			self.hook_error=True
		else:
			if H.vuln:
				self.vuln=True	

	def __launch_test(self):
		# Build each test image
		self.__build_containers()

		# Create Compose Context
		logging.info(colors.colors.OKGREEN\
			+"Constructing Compose Context."\
			+colors.colors.ENDC)
		self.__create_compose_context()
		os.chdir(TMP_FOLDER)

		# Launch Test
		logging.info(colors.colors.OKGREEN\
			+"Running Docker Compose Up"\
			+colors.colors.ENDC)
		dockerw.compose_up()

	def attach(self,container):	
		self.__launch_test()
		from subprocess import call as sh
		container_name = 'xshop_'+self.containers[container]+'_1'
		sh(['docker','exec','-i','-t',container_name,'/bin/bash'])
		self.__clean_test()

	# Runs hooks in test environment
	def run(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)	
		self.log=logging.getLogger()
		self.results = []
		self.vuln = False
		self.hook_error=False
		try:
			print colors.colors.BOLD+"Running Test: "+colors.colors.ENDC+str(self.variables)+", ",
			self.__launch_test()

			# Call hook
			logging.info(colors.colors.OKGREEN+"Running Hooks:"+colors.colors.ENDC)
			self.__call_hooks()					
			if self.hook_error:
				raise Exception("Error Running Hooks")
			else:
				if self.vuln:
					print colors.colors.FAIL+"Vulnerable"+colors.colors.ENDC
				else:
					print colors.colors.OKGREEN+"Invulnerable"+colors.colors.ENDC
				logging.info(colors.colors.OKGREEN+"Result: "+str(self.vuln)+colors.colors.ENDC)
		except Exception as e:
			print colors.colors.BOLD+"ERROR!"+colors.colors.ENDC
			print e
			self.vuln = None

		finally:
			logging.info(colors.colors.OKGREEN+"Cleaning Up."+colors.colors.ENDC)
			self.__clean_test()
			self.__end_logging()

		return self.vuln

#
# 	Decscribes a series of tests with one or more 
#	independent variables
#
class Trial:
	# Accepts ivars and source and saves them as instance variables
	# Recursively builds multidimensional array of test cases
	def __init__(self,ivars):
		self.ivars = ivars
		self.cases = self.__array_builder({},copy.deepcopy(self.ivars))	

	# Recursive function for building array of test cases
	def __array_builder(self,d,ivars):
		# If no more variable dimensions, create test case
		if ivars=={}:
			dnew = copy.deepcopy(d)
			return TestCase(dnew)
		# Else, pop var and return list of recursive call with each value
		else:
			key, value = ivars.popitem()
			l = []
			for v in value:
				dnew = copy.deepcopy(d)
				dnew[key]=v
				l.append(self.__array_builder(dnew,copy.deepcopy(ivars)))
			return l

	# Recursively applies func to TestCases and returns results
	def recursive(self,obj,func):
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
				'vars':o.variables,
				'results':o.results})

	# Builds and tags images for each target container, outputs dockerfiles
	def build(self):
		if not os.path.isdir('build'):
			os.mkdir('build')
		self.recursive(self.cases,lambda o: o.build())
