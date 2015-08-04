#
#	template
#
#		This module provides functions for applying
#		templating to files and folders. The general
#		behavior is for a dictionary of substitutions
# 		to be provided where <%= variable %> is
#		replaced by the value of variable in every
# 		appearance in the file. The function reports
#		if any template elements remain in the file.
#

import jinja2
import os
import shutil
import re

def get_env():
	templateLoader = jinja2.FileSystemLoader( searchpath="." )
	templateEnv = jinja2.Environment( loader=templateLoader )
	return templateEnv

OMIT = '[\s\S]+(.deb$|.tar.gz$|.swp$|.changes$|.dsc$|.tar.xz$|.tar.bz2$)'

def template_file_contents(path,d):
	e = get_env()
	template = e.get_template( path )
	return template.render( d )

#
#	Replaces substitutions within a file. Destructive
#
def template_file(path,d):
	if re.compile('.*Dockerfile').match(path):
		template = env.get_template( path )
		output = template.render( d )
		os.remove(path)
		f = open(path,'w')
		f.write(output)
		f.close()

#
#	Traverses a folder and runs template_file on each
#	file found. Destructive
#
def template_folder(path,d):
	if os.path.isfile(path):
		# File
		if not re.compile(OMIT).match(path):
			template_file(path,d)
	else:
		files = os.listdir(path)
		for f in files:
			template_folder(path+'/'+f,d)	

#
#	Accepts a file or folder `path`, copies it to
#	`output`, and then applies templating in place.
#
def copy_and_template(path,output,d):
	global env
	env = get_env()	
	if os.path.isdir(path):
		# Folder
		shutil.copytree(path,output)
		template_folder(output, d)	
	else:
		# Single File
		shutil.copy2(path,output)
		template_file(output,d)
