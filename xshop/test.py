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
	def __init__(self,results,containers):
		self.error=False
		self.vuln=False
		self.results = results
		self.containers = containers
	def run(self,container,hook):
		result = dockerw.run_hook(self.containers[container],hook)
		self.results.append(result)
		ret = result['ret']
		if not ret==0:
			if ret==2:
				self.vuln=True
			else:
				self.error=True

class TestCase:
	def __init__(self,d,source):
		# Get Project Configuration
		self.config = config.Config()
		self.proj_dir = os.getcwd()
		self.compose = config.parse_docker_compose()
		self.library=self.config.get('library')

		# Build Dictionary of Containers and Their Random Names
		self.containers = {}
		for c in self.compose:
			self.containers[c]=random_name()
		
		# Get Test Case Variables
		self.source = source
		self.d = d

		# Initialize Result Values
		self.vuln=None
		self.results=[]

	# Builds template dict by adding non independent variables
	def __templated(self,name):
		templated = copy.deepcopy(self.d)
		templated['container_name'] = name
		templated['library'] = self.library
		templated['install_type'] = self.source
		templated['builddeps'] = self.config.get('build-dependencies')
		templated['deps']=self.config.get('dependencies')
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
	
		templated = self.__templated(name)	

		# Create temporary build context
		template.copy_and_template("containers/%s"%(name,), 
			TMP_FOLDER,
			templated)

		# Copy in any necessary files
		if name=='target':
			if self.source=='source':
				source_file = "%s/source/%s-%s.tar.gz"%\
					(self.proj_dir, self.library, self.d['version'])
				shutil.copy2(source_file, TMP_FOLDER+"/")
			elif self.source=='debian':
				pkg_dir = "%s/packages/%s-%s/"%\
					(self.proj_dir, self.library, self.d['version'])
				shutil.copytree(pkg_dir, 
					TMP_FOLDER+"/%s-%s"%\
					(self.library, self.d['version'],))

		
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
			# Create Context Folder
			os.mkdir(TMP_FOLDER+"/containers/"+c)
			# Copy in test code
			shutil.copytree(self.proj_dir+'/test',
				TMP_FOLDER+"/containers/"+c+"/test")
			# Write out Dockerfile
			f=open(TMP_FOLDER+"/containers/"+c+"/Dockerfile",'w')
			dockerfile="FROM xshop:%s_build\n"\
					"ADD test /home/\n"\
					"WORKDIR /home/\n"%\
					(v,)

			# Add independent variables to environment
			for key in self.d:
				val = self.d[key]
				if val and not val=='':
					dockerfile=dockerfile+"ENV %s %s\n"%(key,self.d[key])
			
			f.write(dockerfile)
			f.close()

		# Copy in compose, substituting container pseudonyms
		f = open(self.proj_dir+"/docker-compose.yml",'r')
		d = yaml.load(f.read())
		f.close()
		
		newd={}	
	
		for c in d:
			newc = self.containers[c]
			if 'links' in d[c].keys():
				newlinks=[]
				for l in d[c]['links']:
					newlinks.append("%s:%s"%(self.containers[l],l,))
				d[c]['links']=newlinks
			newd[newc]=d[c]
					
	
		f = open(TMP_FOLDER+'/docker-compose.yml','w')
		f.write(yaml.dump(newd))
		f.close()


	# Cleans up logging
	def __end_logging(self):
		for handler in self.log.handlers[:]:
			handler.close()
			self.log.removeHandler(handler)

	#
	# Builds target container as xshop_[library]:[sorted_var_vals]
	# Outputs dockerfile to build/ as Dockerfile_[sorted_var_vals]
	# 
	def build(self):

		logging.basicConfig(filename='build.log',level=logging.DEBUG)	
		self.log=logging.getLogger()
		print colors.colors.BOLD+"Building: "+colors.colors.ENDC+str(self.d)+": ",
		name = '_'.join(map(lambda x: self.d[x],sorted(self.d.keys())))
		image_name='xshop_%s:%s'%(self.library, name)
		try:
			self.__build_container('target',image_name)
			f = open(self.proj_dir+'/build/Dockerfile_'+name,'w')
			f.write(self.dockerfile('target'))
			f.close()
			print colors.colors.OKGREEN+"Done."+colors.colors.ENDC
		except Exception as e:
			print colors.colors.FAIL+"Error!"+colors.colors.ENDC
			print e
		self.__end_logging()

	# Removes temporary test resources
	def __clean_test(self):
		# Terminate Test Containers
		dockerw.compose_down()

		# Remove temporary compose folder
		os.chdir(self.proj_dir)
#		if os.path.isdir(TMP_FOLDER):
#			shutil.rmtree(TMP_FOLDER)	
	
		
		self.__end_logging()

	# Call exploit hook in each container and stores results	
	def __call_hooks(self):
		for c in self.containers:
			logging.info(colors.colors.OKGREEN+"\t"+c+colors.colors.ENDC)
			container = 'xshop_'+c+'_1'
			result=dockerw.run_hook(container,'run_exploit')	
			self.results[c]=result
			if not result['ret']==0:
				if result['ret']==2:
					self.vuln=True
				else:
					self.hook_error=True

	# Runs hooks in test environment
	def run(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)	
		self.log=logging.getLogger()
		self.results = []
		self.vuln = False
		self.hook_error=False
		try:
			print colors.colors.BOLD+"Running Test: "+colors.colors.ENDC+str(self.d)+", ",
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

			# Call hook

			logging.info(colors.colors.OKGREEN+"Running Hooks:"+colors.colors.ENDC)
			sys.path.append(self.proj_dir+"/test")
			import xshop_test
			H = HookRunner(self.results,self.containers)
			xshop_test.run(H)
			if H.error:
				self.hook_error=True
			else:
				if H.vuln:
					self.vuln=True	
					
			if self.hook_error:
				raise Exception("Error Running Hooks")
			else:
				if self.vuln:
					print colors.colors.FAIL+"Vulnerable"+colors.colors.ENDC
				else:
					print colors.colors.OKGREEN+"Invulnerable"+colors.colors.ENDC
				logging.info(colors.colors.OKGREEN+"Result: "+str(self.vuln)+colors.colors.ENDC)
#		except Exception as e:
#			print colors.colors.BOLD+"ERROR!"+colors.colors.ENDC
#			print e
#			self.vuln = None

		finally:
			logging.info(colors.colors.OKGREEN+"Cleaning Up."+colors.colors.ENDC)
			self.__clean_test()

		return self.vuln

#
# 	Decscribes a series of tests with one or more 
#	independent variables
#
class Trial:
	# Accepts ivars and source and saves them as instance variables
	# Recursively builds multidimensional array of test cases
	def __init__(self,ivars,source):
		self.ivars = ivars
		self.source = source
		self.cases = self.__array_builder({},copy.deepcopy(self.ivars))	

	# Recursive function for building array of test cases
	def __array_builder(self,d,ivars):
		# If no more variable dimensions, create test case
		if ivars=={}:
			dnew = copy.deepcopy(d)
			return TestCase(dnew,self.source)
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
		results=[]
		for o in obj:
			if isinstance(o,list):
				results.append(self.recursive(o,func))
			else:
				results.append(func(o))
		return results

	# Runs a test case for each value
	def run(self):
		self.recursive(self.cases,lambda o: o.run())

	# Return results of all test cases by calling recursive function. 
	def results(self):
		return self.recursive(self.cases,
			lambda o: {
				'vuln': o.vuln,
				'vars':o.d,
				'results':o.results})

	# Builds and tags images for each target container, outputs dockerfiles
	def build(self):
		if not os.path.isdir('build'):
			os.mkdir('build')
		self.recursive(self.cases,lambda o: o.build())
