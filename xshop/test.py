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

import logging
from xshop import exceptions
from xshop import template
from xshop import dockerw
from xshop import config
import shutil
import os
import re

#
#	This function assembles the build context for a given 
#	container. It creates a temporary context, copies in
#	relevant files and populates the template with values.
#
def build_context(name,d):
	d['container_name']=name
	
	# Copy folder and apply template
	template.copy_and_template('containers/'+name, 'build-tmp/containers/'+name,d)

	# Copy in test folder
	shutil.copytree('test','build-tmp/containers/'+name+'/test')

#
#	A rudimentary attempt to parse only the names of 
#	containers from a docker-compose.yml file without
#	having to add a yaml parsing library.
#
def parse_docker_compose():
	regex = re.compile("^([\S]+):\n")

	containers = []
	f = open('docker-compose.yml')
	for line in f.readlines():
		m = regex.match(line)
		if m:	
			containers.append(m.group(1))
	return containers

#
#	This function reads in the docker-compose.yml and uses
#	build_context() to construct each of the required
#	contexts.
#
def prepare_build(containers,d):
	# Create temporary compose folder
	os.mkdir('build-tmp')
	os.mkdir('build-tmp/containers')

	# Copy docker-compose.yml
	shutil.copy2('docker-compose.yml','build-tmp/docker-compose.yml')

	# Constuct each context
	for container in containers:
		build_context(container,d)
	
	# Move into temporary directory
	os.chdir('build-tmp')

#
# 	This function reads the docker-compose.yml and cleans
# 	up any ephemeral contexts, containers, or images that 
#	may be created during a test
#
def clean_build(containers):
	# Remove temporary compose folder
	shutil.rmtree('build-tmp')

#
#	This function is intended to be the main script for i
#	running a test.
#
def run_test(version,install_type):
	logging.basicConfig(filename='test.log',level=logging.DEBUG)	
	
	if not config.check():
		raise Exception('No project configuration found')

	library = config.Config().get('library')
	
	cwd = os.getcwd()
	
	try:
		#TODO Check version available

		# Get containers
		containers = parse_docker_compose()
		
		# Generate template dictionary	
		d = {'library':library,
			'version':version,
			'install_type':install_type}

		# Prepare Build
		prepare_build(containers,d)

		# Check for base test image	
		dockerw.build_image('base_test_image')

		# Run Docker Compose
		dockerw.compose_up()

		# Call hook
		vuln=False
		for c in containers:
			c = "xshop_"+c+"_1"
			if dockerw.run_hook(c,'run_exploit'):
				vuln=True
			# TODO - Change hook to check environment variable

	except exceptions.DockerError as e:
		raise exceptions.DockerError(e)
	finally:
		os.chdir(cwd)
		# Clean up
		clean_build(containers)
	
	return vuln
