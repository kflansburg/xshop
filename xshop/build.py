#
#	build
#
#		This module provides functions to build packages
#		within a container environment. 
#

from xshop import dockerw
import logging
from subprocess import Popen as sh

#
#	Constructs a base cowbuilder image
#
def base_build_image():
	dockerw.build_image('base_build_image')

	# Cowbuilder must be installed in privileged container
	dockerw.run_privileged('xshop:base_build_image','xshop:build_image',['cowbuilder','--create'])		
	
	

#
#	Function to perform build on a given version tarball in
# 	/source and output resulting package to /packages
#
def build(version):
	logging.basicConfig(filename='build.log',level=logging.DEBUG)

	if not dockerw.image_exists('xshop:build_image'):	
		base_build_image()

	# Check that source exists
	# Contruct build context

	# Construct build image

	# Run pbuilder

	# Run Lintian

	# If success, copy out result and return lintian

	pass
