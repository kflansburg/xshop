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
#		|- config.yaml
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
#		|-config.yaml
#		|-source
#		|-packages
#		|-config
#		|	|-debian
#		|	|	|-changelog
#		|	|	|-rules
#		|	|	|-control
#		|	|-.pbuilderrc
#

import os
import shutil
from xshop import config

#
#	Generates a new directory, `name` with the required
#	structure for a test project as described above and 
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
	
	# Copy in default files
	xshop_path = os.path.dirname(os.path.realpath(__file__))
	shutil.copy2(xshop_path+"/defaults/docker-compose-test-default.yml",name+'/docker-compose.yml')
	shutil.copy2(xshop_path+"/defaults/xshop_test-default.py",name+'/test/xshop_test.py')
	shutil.copy2(xshop_path+"/defaults/Dockerfile-test-attacker-default",name+'/containers/attacker/Dockerfile')
	shutil.copy2(xshop_path+"/defaults/Dockerfile-test-target-default",name+'/containers/target/Dockerfile')

	os.chdir(name)
	c = config.Config()
	c.put('library',library)	
	os.chdir('..')

#
#	Generates a new directory, `name` with the required
#	structure for a build project as described above and 
#	copies any templates in. 
#
def new_build_project(library, name):
	if os.path.isdir(name) or os.path.isfile(name):
		raise OSError('Folder %s already exists'%(name,))

	os.mkdir(name)
	os.mkdir(name+"/source")
	os.mkdir(name+"/packages")
	os.mkdir(name+"/config")
	os.mkdir(name+"/config/debian")

	xshop_path = os.path.dirname(os.path.realpath(__file__))
	
	shutil.copy2(xshop_path+"/defaults/debian/changelog", name+"/config/debian/changelog")
	shutil.copy2(xshop_path+"/defaults/debian/control", name+"/config/debian/control")
	shutil.copy2(xshop_path+"/defaults/debian/rules", name+"/config/debian/rules")

	os.chdir(name)
	c = config.Config()
	c.put('library', library)
	c.put('upstream-url',None)
	c.put('dependencies',[])
	c.put('build-dependencies',[])
	c.put('name', None)
	c.put('email', None)
	c.put('source-versions', [])
	c.put('built-versions',[])
	os.chdir('..')
