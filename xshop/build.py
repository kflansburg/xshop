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
from xshop import versionmanager
import logging
from subprocess import Popen as sh
import os
import shutil
from sets import Set
from xshop import colors

TMP_FOLDER='build-tmp'

#
#	Collects build config into dictionary for templating
#
def build_template_dict(c,var):
        d = {'library':c.get('library'),
                'name':c.get('name'),
                'email':c.get('email'),
                'builddeps':c.get('build-dependencies'),
                'deps':c.get('dependencies')}
	for key in var:
		d[key]=var[key]
	return d

#
#	Removes any directories that will be used for this build
#
def clean(output_path):
        if os.path.isdir(output_path):
                shutil.rmtree(output_path)

        if os.path.isdir(TMP_FOLDER):
                shutil.rmtree(TMP_FOLDER)

#
#	Copies files used to build into context
#
def make_build_context(d,source_path):
	# Copy and template build/ to build-tmp/
	template.copy_and_template('build',TMP_FOLDER,d)

	# Copy in Tarball
        shutil.copy2(source_path,TMP_FOLDER+'/')
        

#
#	Copies out deb
#
def copy_build_result(deb_path,pkg_path):
	deb_path = 'xshop_lintian:'+deb_path
	dockerw.run_docker_command(['docker','cp',deb_path,pkg_path])

def run_lintian(deb_path):
	try:
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
def build(d):

	# Get project config
	c = config.Config()
	library = c.get('library')
	version = d['version']
	templated = build_template_dict(c,d)

	# Directory to place packages in 
	deb_path = '/home/'+library+'-'+version+'/'+library+'_'+version+'-1_amd64.deb'
	source_path = 'source/'+library+'-'+version+'.tar.gz'
	pkg_path = 'packages/'+library+'_'+'_'.join(map(lambda x: d[x], sorted(d.keys()))) 

	# Check that tarball is available
	versions = versionmanager.detect_source(library,'source') 
	if not version in versions:
		raise exceptions.BuildError('Source version '+version+' not found in source folder.')
	
	
	print colors.colors.BOLD+"Packaging "+version+": "+colors.colors.ENDC,
	
	# Clean old files
	clean(pkg_path)

	try:
		# Construct build context
		make_build_context(templated,source_path)
	
		# Construct build image
		dockerw.run_docker_command(['docker','build','-t','xshop:build-tmp',TMP_FOLDER+'/'])

		try:
			run_lintian(deb_path)
		except exceptions.LintianError as e:
			logging.error(e)
			print colors.colors.FAIL+"Lintian Failed"+colors.colors.ENDC,

		copy_build_result(deb_path,pkg_path)
		print colors.colors.BOLD+"Done!"+colors.colors.ENDC,
	finally:
		shutil.rmtree(TMP_FOLDER)

def build_all():
	c = config.Config()
	sversions = versionmanager.detect_source(c.get('library'),'source') 
	# Build each version and if it succeeds, add to build versions list. 
	# Wrap in try to prevent errors from stopping the build. 
	for v in sversions:
		try:
			build({'version':v})
			print ""
		except Exception as e:
			print colors.colors.FAIL+"FAILED :("+colors.colors.ENDC
			print(e)
