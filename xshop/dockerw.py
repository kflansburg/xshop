#
#	dockerw
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
from xshop import test
from xshop.loggerwrapper import LoggerWriter
import subprocess
from subprocess import Popen as sh

#
#	Checks whether a container name exists, running
#	or not
#
def container_exists(name,all=True):
	c = Client(base_url='unix://var/run/docker.sock')
	containers = c.containers(all=all)
	for container in containers:
		names = container["Names"]
		for n in names:
			if n=='/'+name or n == name or n==name+"\\":
				return True
	return False

#
#	Wrapper for easily checking if container is running
#
def container_running(name):
	return container_exists(name,all=False)

#
#	Checks whether an image exists
#
def image_exists(name):
	c = Client(base_url='unix://var/run/docker.sock')
	images = c.images()
	for image in images:
		tags = image['RepoTags']
		for tag in tags:
			if tag==name:
				return True
	return False

#
# 	Calls docker compose on a supplied compose file
#
def compose_up():
	#TODO check for errors from docker
	process = sh(['docker-compose','-p','xshop','build'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	output,_ = process.communicate()
	logging.info(output)
	process = sh(['docker-compose','-p','xshop','up','-d'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	output,_ = process.communicate()
	logging.info(output)

#
#	Function to clean up a test environemnt
#
def compose_down():
	#TODO check for errors from docker
	# Get list of project containers
	containers = test.parse_docker_compose()
	
	# Kill each one. Docker-compose kill can be ineffective
	containers = map(lambda c: "xshop_"+c+"_1", containers)
	for c in containers:
		process = sh(['docker','kill',c],stdout=subprocess.PIPE)	
		output,_ = process.communicate()
		logging.info(output)

#
#	Runs a given hook in a running container and return
#	results
#
def run_hook(container,hook):
	#TODO Test
	if not container_running(container):
		raise DockerError('Container '+container+' not running, cannot run hook')
	
	c = Client(base_url='unix://var/run/docker.sock')

	# Create exec
	job = c.exec_create(container, 'python2 -c "import test;import sys;sys.exit(test.'+hook+'())')	

	# Run 	
	for line in c.exec_start(job,stream=True):
		logging.info(line)

	print c.exec_inspect(job)
	
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
