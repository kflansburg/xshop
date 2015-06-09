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

import os
import shutil

#
#	Generates a new directory, `name` with the required
#	structure for a test project as described above and 
#	copies any templates in. 
#

def new_test_project(name):
	if os.path.isdir(name) or os.path.isfile(name):
		raise OSError('Folder %s already exists'%(name,))


	# Folder Structure
	os.mkdir(name)
	os.mkdir(name+"/containers")
	os.mkdir(name+"/containers/target")
	os.mkdir(name+"/containers/attacker")
	os.mkdir(name+"/test")
	
	# Copy in default files
#
#	Generates a new directory, `name` with the required
#	structure for a build project as described above and 
#	copies any templates in. 
#
def new_build_project(name):
	if os.path.isdir(name) or os.path.isfile(name):
		raise OSError('Folder %s already exists'%(name,))

	os.mkdir(name)
	os.mkdir(name+"/source")
	os.mkdir(name+"/packages")
	os.mkdir(name+"/config")
