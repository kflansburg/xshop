#
#	exceptions
#
#		This module provides more descriptive custom exceptions.
#

#
#	Thrown when the docker daemon reports an error with a command
#
class DockerError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)