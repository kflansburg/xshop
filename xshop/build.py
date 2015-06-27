#
#	build
#
#		This module provides functions to build packages
#		within a container environment. 
#

from xshop import template
from xshop import exceptions
from xshop import dockerw
from xshop import config
import logging
from subprocess import Popen as sh
import os
import shutil
from sets import Set
from xshop import colors

#
#	Collects build config into dictionary for templating
#
def build_template_dict(c,version):
        d = {'library':c.get('library'),
                'name':c.get('name'),
                'email':c.get('email'),
                'builddeps':c.get('build-dependencies'),
                'deps':c.get('dependencies'),
                'version':version}
	return d

#
#	Removes any directories that will be used for this build
#
def clean(output_path):
        if os.path.isdir(output_path):
                shutil.rmtree(output_path)

        if os.path.isdir('build-tmp'):
                shutil.rmtree('build-tmp')

#
#	Verifies that source file is available
#
def check_source(library, version):
	source_path = 'source/'+library+'-'+version+'.tar.gz'
	if not os.path.isfile(source_path):
		raise Exception('The source tarball could not be found in source/')

#
#	Copies files used to build into context
#
def make_build_context(d):
	# Copy and template build/ to build-tmp/
	template.copy_and_template('build','build-tmp',d)

	# Copy in Tarball
	source_path = 'source/'+d['library']+'-'+d['version']+'.tar.gz'
        shutil.copy2(source_path,'build-tmp/')
        

#
#	Copies out deb
#
def copy_build_result(library,version):
	output_path = 'packages/'+library+'-'+version+'/'
	deb_path = 'xshop_lintian:/home/'+library+'-'+version+'/'+library+'_'+version+'-1_amd64.deb'
	dockerw.run_docker_command(['docker','cp',deb_path,output_path])

def run_lintian(library,version):
	try:
		deb_path = '/home/'+library+'-'+version+'/'+library+'_'+version+'-1_amd64.deb'
		dockerw.remove_container('xshop_lintian')
		dockerw.run_docker_command(['docker',
                        'run',
                        '--name=xshop_lintian',
                        'xshop:build-tmp',
                        'lintian',
                        deb_path])
	except exceptions.DockerError as e:
		raise exceptions.LintianError('')	

#
#	Function to perform build on a given version tarball in
# 	/source and output resulting package to /packages
#
def build(version):

	# Get project config
	c = config.Config()
	library = c.get('library')

	# Assemble template dictionary
	d = build_template_dict(c,version)
	
	output_path = 'packages/'+library+'-'+version

	# Clean old files
	clean(output_path)

	try:
		# Check that source exists
		check_source(library,version)
	
		# Construct build context
		make_build_context(d)
		
		# Construct build image
		dockerw.run_docker_command(['docker','build','-t','xshop:build-tmp','build-tmp/'])

	finally:
		shutil.rmtree('build-tmp')

def finish_logging(library,version,log):
	handlers = log.handlers[:]
	for handler in handlers:
    		handler.close()
    		log.removeHandler(handler)
	if not os.path.isdir('packages/'+library+'-'+version):
		os.mkdir('packages/'+library+'-'+version)
	shutil.move('build.log','packages/'+library+'-'+version+'/build.log')

def build_version(version):
	c = config.Config()
	library = c.get('library')
	logging.basicConfig(filename='build.log',level=logging.DEBUG)
	log = logging.getLogger()
	print colors.colors.BOLD+"Packaging "+version+": "+colors.colors.ENDC,
	try:
		build(version)
		print colors.colors.BOLD+"Build - "+colors.colors.OKGREEN+"Success. "+colors.colors.ENDC,
	except exceptions.BuildError as e:
		print colors.colors.BOLD+"Build - "+colors.colors.FAIL+"Failed."+colors.colors.ENDC
		finish_logging(library,version,log)
		return False

	try:
		run_lintian(library,version)
		print colors.colors.BOLD+"Lintian - "+colors.colors.OKGREEN+"Success."+colors.colors.ENDC,
	except exceptions.LintianError as e:
		print colors.colors.BOLD+"Lintian - "+colors.colors.FAIL+"Failed."+colors.colors.ENDC,
	
	try:
		copy_build_result(library, version)
		print colors.colors.BOLD+"Copying Results - "+colors.colors.OKGREEN+"Success."+colors.colors.ENDC
	except exceptions.DockerError as e:
		print colors.colors.BOLD+"Copying Results - "+colors.colors.FAIL+"Failed."+colors.colors.ENDC
		finish_logging(library,version,log)
		return False

	finish_logging(library,version,log)
	return True


def build_multiple(rebuild):
	c = config.Config()
	sversions = Set(c.get('source-versions'))
	bversions = c.get('built-versions')
	if rebuild:
		versions = sversions
		bversions = []
		c.put('built-versions',bversions)
	else:
		versions = sversions - Set(bversions)

	print "Found source for :\n"+str(list(sversions))
	versions = list(versions)
	print "Building versions:\n"+str(versions)

	# Build each version and if it succeeds, add to build versions list. 
	# Wrap in try to prevent errors from stopping the build. 
	for v in versions:
		try:
			if build_version(v):
				bversions.append(v)
				c.put('built-versions',bversions)
		except Exception as e:
			print(e)

				
