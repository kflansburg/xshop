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
#	Constructs a base cowbuilder image
#
def base_build_image():
	dockerw.build_image('base_build_image')

	# Cowbuilder must be installed in privileged container
	dockerw.run_privileged('xshop:base_build_image','xshop:build_image',['cowbuilder','--create'])		
	
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
def clean(path):
        if os.path.isdir(path):
                shutil.rmtree(path)

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
	source_path = 'source/'+d['library']+'-'+d['version']+'.tar.gz'
	
	# Copy in Tarball
        shutil.copy2(source_path,'build-tmp/')
        
	# Copy in build Dockerfile
	xshop_path =os.path.abspath(os.path.dirname(__file__))
	template.copy_and_template(xshop_path+'/defaults/Dockerfile-build-default','build-tmp/Dockerfile',d)

	# Copy in debian files
	template.copy_and_template('config/debian','build-tmp/debian',d)

#
#	Copies out pbuilder result folder
#
def copy_build_result(output_path):
	dockerw.run_docker_command(['docker','cp','xshop_privileged_run:/var/cache/pbuilder/result','packages/'])
	shutil.move('packages/result',output_path)

def run_lintian(version):
	c = config.Config()
	library = c.get('library')
	ERROR=False
	try:
		dockerw.remove_container('xshop_lintian')
		dockerw.run_docker_command(['docker',
                        'run',
                        '--name=xshop_lintian',
                        'xshop:build-final',
                        'lintian',
                        '/var/cache/pbuilder/result/'+library+'_'+version+'-1.dsc'])
	except exceptions.DockerError as e:
		logging.warning(e)
		ERROR=True

	try:
		dockerw.remove_container('xshop_lintian')
		dockerw.run_docker_command(['docker',
                        'run',
                        '--name=xshop_lintian',
                        'xshop:build-final',
                        'lintian',
                        '/var/cache/pbuilder/result/'+library+'_'+version+'-1_amd64.deb'])
	except exceptions.DockerError as e:
		logging.warning(e)
		ERROR=True

	if ERROR:
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

	os.mkdir('build-tmp')

	try:
		# Build base image if neccesary
		if not dockerw.image_exists('xshop:build_image'):	
			base_build_image()

		# Check that source exists
		check_source(library,version)
	
		# Construct build context
		make_build_context(d)
		
		# Construct build image
		dockerw.run_docker_command(['docker','build','-t','xshop:build-tmp','build-tmp/'])

		# Run pbuilder
		try:
			dockerw.run_privileged('xshop:build-tmp','xshop:build-final',[])
		except exceptions.DockerError as e:
			raise exceptions.BuildError(e)
		
		# Copy out results
		copy_build_result(output_path)

	finally:
		shutil.rmtree('build-tmp')
		if not os.path.isdir('packages/'+d['library']+'-'+d['version']):
			os.mkdir('packages/'+d['library']+'-'+d['version'])
		shutil.move('build.log','packages/'+d['library']+'-'+d['version']+'/build.log')

def finish_logging(log):
	handlers = log.handlers[:]
	for handler in handlers:
    		handler.close()
    		log.removeHandler(handler)

def build_version(version):
	logging.basicConfig(filename='build.log',level=logging.DEBUG)
	log = logging.getLogger()
	print colors.colors.BOLD+"Packaging "+version+": "+colors.colors.ENDC,
	try:
		build(version)
		print colors.colors.BOLD+"Build - "+colors.colors.OKGREEN+"Success. "+colors.colors.ENDC,
	except exceptions.BuildError as e:
		print colors.colors.BOLD+"Build - "+colors.colors.FAIL+"Failed."+colors.colors.ENDC
		finish_logging(log)
		return False

	try:
		run_lintian(version)
		print colors.colors.BOLD+"Lintian - "+colors.colors.OKGREEN+"Success."+colors.colors.ENDC
	except exceptions.LintianError as e:
		print colors.colors.BOLD+"Lintian - "+colors.colors.FAIL+"Failed."+colors.colors.ENDC
		finish_logging(log)
		return False
	finish_logging(log)
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

				
