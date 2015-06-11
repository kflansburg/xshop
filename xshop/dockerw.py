#
#	docker
#
#		This module provides some conveniance classes
#		for interacting with docker. In most cases
#		this is a wrapper for common tasks which 
#		attempts to be responsible for error handling
#		and make switching between the docker python
#		library and the docker command line utility
#		transparent. 
#
#		As a rule, this module favors the docker
#		python library except where there is a gap
#		in functionality. 
#

import logging
import os
from docker import Client
import json
from xshop import exceptions

#
#	Checks whether a container name exists, running
#	or not
#
def container_exists():
	pass

#
#	Checks whether an image exists
#
def image_exists():
	pass

#
# 	Calls docker compose on a supplied compose file
#
def compose_up():
	pass

#
#	Runs a given hook in a running container and return
#	results
#
def run_hook():
	pass

#
#	Build contexts for some default images to be used are 
# 	stored in xshop/defaults/contexts/<image_name>. This
#	function builds the specified image. 
#
def build_image(image_name):
	xshop_path = os.path.dirname(os.path.realpath(__file__))
	context_path = xshop_path+"/defaults/contexts/"+image_name

	# Check that a build context exists
	if not os.path.isdir(context_path):
		raise IOError('Image context not found')
	if not os.path.isfile(context_path+"/Dockerfile"):
		raise IOError('Dockerfile not found in context')

	# Call docker build, catching errors
	c = Client(base_url='unix://var/run/docker.sock')
	c.ping()
	for line in c.build(path=context_path, rm=True, tag='xshop:'+image_name):
		d = json.loads(line)
		if 'stream' in d:		
			logging.info(d['stream'])
		if 'error' in d:
			logging.critical(d['error'])
			raise exceptions.DockerError('Building '+image_name+' failed: '+d['error'])
