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

#
#	This function assembles the build context for a given 
#	container. It creates a temporary context, copies in
#	relevant files and populates the template with values.
#
def build_context():
	pass

#
#	This function reads in the docker-compose.yml and uses
#	build_context() to construct each of the required
#	contexts.
#
def prepare_build():
	pass

#
#	This function is intended to be the main script for i
#	running a test.
#
def run_test():
	pass
