#
#	Test
#
#		The purpose of this module is to provide functions
#		which carry out verious testing scenarios. The 
#		default test works as follows:
#	
#		Duplicate the docker compose context
#
#		Apply templating to populate values
#
#		Copy testing scripts into all build contexts
#	
#		Call docker compose to set up the test environment
#		
#		Call testing hooks for specified container
#
#		Return results of test and clean up
#

import copy
import logging
from xshop import build
from xshop import colors
from xshop import exceptions
from xshop import template
from xshop import dockerw
from xshop import config
import shutil
import os
import re

TMP_FOLDER='test-tmp'

class TestCase:
	def __init__(self,d,source):
		# Get Project Configuration
		self.config = config.Config()
		self.proj_dir = os.getcwd()
		self.compose = config.parse_docker_compose()
		self.containers = [c for c in self.compose]
		self.library=self.config.get('library')
		
		# Get Test Case Variables
		self.source = source
		self.d = d
		self.pkgdir=self.proj_dir+'/packages/'+self.library+'_'+'_'.join(map(lambda x: d[x], sorted(d.keys())))
	
	# Creates Docker context for a given container in the test
	# environment.
	def __build_context(self,name):
		# Create Templating Dictionary
		templated = copy.deepcopy(self.d)
		templated['container_name']=name
		templated['library']=self.library
		templated['install_type']=self.source
	
		# Copy folder and apply template
		template.copy_and_template('containers/'+name,
			TMP_FOLDER+'/containers/'+name,
			templated)

		# Copy in test folder
		shutil.copytree('test',TMP_FOLDER+'/containers/'+name+'/test')

		# If install source is debian, copy it into target context	
		if self.source=='debian' and name=='target':
			shutil.copytree(self.pkgdir, 
				TMP_FOLDER+'/containers/target/'+self.library+'-'+templated['version'])

	# Creates temporary build dir and constructs contexts for
	# each container in the experiment inside
	def __prepare_build(self):
		os.mkdir(TMP_FOLDER)
		os.mkdir(TMP_FOLDER+'/containers')

		# Copy docker-compose.yml
		shutil.copy2('docker-compose.yml',TMP_FOLDER+'/docker-compose.yml')

		# Constuct each context
		for c in self.containers:
			self.__build_context(c)
	
		# Move into temporary directory
		os.chdir(TMP_FOLDER)
	
	# Removes temporary build directory
	def __clean(self):
		# Remove temporary compose folder
		os.chdir(self.proj_dir)
		if os.path.isdir(TMP_FOLDER):
			shutil.rmtree(TMP_FOLDER)
	
		# Terminate Test Containers
		dockerw.compose_down()
		
		# End any logging
		for handler in self.log.handlers[:]:
			handler.close()
			self.log.removeHandler(handler)

	# Call exploit hook in each container	
	def __call_hooks(self):
		for c in self.containers:
			logging.info(colors.colors.OKGREEN+"\t"+c+colors.colors.ENDC)
			container = 'xshop_'+c+'_1'
			result=dockerw.run_hook(container,'run_exploit')	
			self.results[c]=result
			if result['ret']==2:
				self.vuln=True

	# Runs hooks in test environment
	def run(self):
		logging.basicConfig(filename='test.log',level=logging.DEBUG)	
		self.log=logging.getLogger()
		self.results = {}
		self.vuln = False
		try:
			# If install type is source, build it
			if self.source=='source':
				self.source='debian'
				build.build(self.d)
		
			# Prepare Build
			logging.info(colors.colors.OKGREEN+"Preparing Build Context."+colors.colors.ENDC)
			self.__prepare_build()

			# Check for base test image	
			logging.info(colors.colors.OKGREEN+"Rebuilding Base Test Image."+colors.colors.ENDC)
			dockerw.build_image('base_test_image')

			# Run Docker Compose
			dockerw.compose_up()

			# Call hooks in each container, catching any exceptions
			logging.info(colors.colors.OKGREEN+"Running Hooks:"+colors.colors.ENDC)
			self.__call_hooks()
			logging.info(colors.colors.OKGREEN+"Result: "+str(self.vuln)+colors.colors.ENDC)

		finally:
			logging.info(colors.colors.OKGREEN+"Cleaning Up."+colors.colors.ENDC)
			# Clean up
			self.__clean()

		return self.vuln

#
# 	Decscribes a series of tests with one or more 
#	independent variables
#
class Trial:
	def __init__(self,cvars,ivars,source):
		self.ivars = ivars
		self.cvars = cvars
		self.source = source
		
		self.cases = self.__array_builder({},copy.deepcopy(self.ivars))	

	def __array_builder(self,d,ivars):
		if ivars=={}:
			dnew = copy.deepcopy(d)
			dnew.update(self.cvars)
			return {'vars':d,'case':TestCase(dnew,self.source)}
		else:
			key, value = ivars.popitem()
			l = []
			for v in value:
				dnew = copy.deepcopy(d)
				dnew[key]=v
				l.append(self.__array_builder(dnew,copy.deepcopy(ivars)))
			return l
	def __run_tests(self,obj):
		for o in obj:
			if isinstance(o,list):
				self.__run_tests(o)
			else:
				case = o['case']
				d = o['vars']
				print colors.colors.BOLD+"Running Test: "+colors.colors.ENDC+str(d)+", ",
				if case.run():
					print colors.colors.FAIL+"Vulnerable"+colors.colors.ENDC
				else:
					print colors.colors.OKGREEN+"Invulnerable"+colors.colors.ENDC

	# Runs a test case for each value
	def run(self):
		self.__run_tests(self.cases)

