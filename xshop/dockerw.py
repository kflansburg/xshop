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
from xshop import colors
import subprocess
import re
import sys
from subprocess import Popen as sh

# 	
#	Runs a docker command and handles any errors
#
def run_docker_command(command):
	process = sh(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        while process.poll() is None:
                logging.info(process.stdout.readline())

        stdout,stderr = process.communicate()
        logging.info(stdout)
        if process.returncode:
                raise exceptions.DockerError(stderr)


#
#	Helper function to parse docker compose yaml
#
def parse_docker_compose():
        regex = re.compile("^([\S]+):\n")

        containers = []
        f = open('docker-compose.yml')
        for line in f.readlines():
                m = regex.match(line)
                if m:
                        containers.append(m.group(1))
        return containers

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
#	Kills and removes a container if it exists
#
def remove_container(c):
	if container_exists(c):
		run_docker_command(['docker','kill',c])
		run_docker_command(['docker','rm',c])

#
#	Removes image if it exists
#
def remove_image(c):
	if image_exists(c):
		run_docker_command(['docker','rmi',c])

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
	logging.info(colors.colors.OKGREEN+"Running docker-compose build"+colors.colors.ENDC)
	run_docker_command(['docker-compose','-p','xshop','build'])
	logging.info(colors.colors.OKGREEN+"Running docker-compose start"+colors.colors.ENDC)
	run_docker_command(['docker-compose','-p','xshop','up','-d'])

#
#	Function to clean up a test environemnt
#
def compose_down():
	# Get list of project containers
	containers = parse_docker_compose()
	
	# Kill each one. Docker-compose kill can be ineffective
	containers = map(lambda c: "xshop_"+c+"_1", containers)
	for c in containers:
		remove_container(c)

#
#	Runs a given hook in a running container and return
#	results
#
def run_hook(container,hook):
	if not container_running(container):
		raise exceptions.DockerError('Container '+container+' not running, cannot run hook')
	
	c = Client(base_url='unix://var/run/docker.sock')

	# Create exec
	job = c.exec_create(container, 'python2 -c "import xshop_test;import sys;sys.exit(xshop_test.'+hook+'())"')	

	# Run 	
	for line in c.exec_start(job,stream=True):
		logging.info(line)

	return c.exec_inspect(job)['ExitCode']
	
def run_privileged(input_image, output_image, command):
	remove_container('xshop_privileged_run')	
	run_docker_command(['docker','run','--privileged=true','--name=xshop_privileged_run',input_image]+command)
	run_docker_command(['docker','commit','xshop_privileged_run', output_image])

#
#	Build contexts for some default images to be used are 
# 	stored in xshop/defaults/contexts/<image_name>. This
#	function builds the specified image. 
#
def build_image(image_name):
	xshop_path =os.path.abspath(os.path.dirname(__file__))
	context_path = xshop_path+"/defaults/contexts/"+image_name

	# Check that a build context exists
	if not os.path.isdir(context_path):
		raise IOError('Image context not found:' + context_path)
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
