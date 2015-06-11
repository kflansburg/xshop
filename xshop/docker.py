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
#	Builds a specified dockerfile
#
def build_image():
	pass
