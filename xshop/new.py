#
#	new
#
#		The goal of this module is to provide functions for
#		creating the directory structure and copying 
#		templates into new projects. 
#
#		Projects include Test and Build projects.
#
#		The structure for Test Project:
#
#		PROJECT_NAME
#		|- docker-compose.yml
#		|- containers
#		|	|- target
#		|	|	|- Dockerfile
#		|	|- attacker
#		|	|	|- Dockerfile
#		|- test
#		|	|- test.py
#
#		The structure for a Build Project:
#
#		PROJECT_NAME
#		|-source
#		|-packages
#		|-config
#		|	|-debian
#		|	|-.pbuilderrc
#

#
#	Generates a new directory, `name` with the required
#	structure for a test project as described above and 
#	copies any templates in. 
#

def new_test_project(name):
	pass

#
#	Generates a new directory, `name` with the required
#	structure for a build project as described above and 
#	copies any templates in. 
#
def new_build_project(name):
	pass
