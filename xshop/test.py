#
#	Test
#
#		The purpose of this module is to provide functions
#		which carry out verious testing scenarios. The 
#		default test works as follows:
#	
#		Call docker compose to set up the test environment
#		
#		Call testing hooks for specified container
#
#		Return results of test and clean up
#

from xshop import template
import shutil

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
#	This function reads in the docker-compose.yml and uses
#	build_context() to construct each of the required
#	contexts.
#
def prepare_build():
	# Create temporary compose folder
	# Copy docker-compose.yml
	# Constuct each context
	pass

#
# 	This function reads the docker-compose.yml and cleans
# 	up any ephemeral contexts, containers, or images that 
#	may be created during a test
#
def clean_build():
	# Remove temporary compose folder
	# Remove containers created
	pass

#
#	This function is intended to be the main script for i
#	running a test.
#
def run_test():
	# Prepare Build
	# Call hook
	# Clean up
	pass
