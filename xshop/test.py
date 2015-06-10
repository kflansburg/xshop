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

from xshop import template
import shutil
import os
import re

#
#	This function assembles the build context for a given 
#	container. It creates a temporary context, copies in
#	relevant files and populates the template with values.
#
def build_context(name,d):
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
	# Copy docker-compose.yml
	shutil.copy2('docker-compose.yml','build-tmp/docker-compose.yml')

	# Constuct each context
	for container in containers:
		os.mkdir('build-tmp/'+container)
		build_context(container,d)
	
	# Move into temporary directory
	os.chdir('build.tmp')

#
# 	This function reads the docker-compose.yml and cleans
# 	up any ephemeral contexts, containers, or images that 
#	may be created during a test
#
def clean_build(containers):
	# Remove temporary compose folder
	os.chdir('..')
	shutil.rmtree('build-tmp')

#
#	This function is intended to be the main script for i
#	running a test.
#
def run_test():
	# Prepare Build
	# Call hook
	# Clean up
	pass
