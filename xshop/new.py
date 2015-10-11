#
#	new
#
#		The goal of this module is to provide functions for
#		creating the directory structure and copying 
#		templates into new projects. 
#
#		The folder structure:
#
#		PROJECT_NAME
#		|- config.yaml
#		|- docker-compose.yml
#		|- containers
#		|	|- target
#		|	|	|- Dockerfile
#		|	|- attacker
#		|	|	|- Dockerfile
#		|- test
#		|	|- test.py
#		|- build
#		|  |- Dockerfile
#		|- source
#		|- packages
#

import os
import shutil
from xshop import config

#
#	Generates a new directory, `name` with the required
#	structure for a project as described above and 
#	copies any templates in. 
#

def new_test_project(library, name):
	if os.path.isdir(name) or os.path.isfile(name):
		raise OSError('Folder %s already exists'%(name,))

	# Folder Structure
	os.mkdir(name)
	os.mkdir(name+"/containers")
	os.mkdir(name+"/containers/target")
	os.mkdir(name+"/containers/attacker")
	os.mkdir(name+"/test")
	os.mkdir(name+"/source")
	os.mkdir(name+"/packages")

	# Copy in default files
	xshop_path = os.path.dirname(os.path.realpath(__file__))
	shutil.copy2(xshop_path
		+ "/defaults/docker-compose-test-default.yml",
		name+'/docker-compose.yml')
	shutil.copy2(xshop_path
		+ "/defaults/xshop_test-default.py",
		name+'/test/xshop_test.py')
	shutil.copy2(xshop_path
		+ "/defaults/Dockerfile-test-attacker-default",
		name+'/containers/attacker/Dockerfile')
	shutil.copy2(xshop_path
		+ "/defaults/Dockerfile-test-target-default",
		name+'/containers/target/Dockerfile')

	os.chdir(name)
	config.generate_new_config(library)
	os.chdir('..')

