"""
    Exceptions Module
        
        Custom exceptions used by XShop
"""

class ProviderError(Exception):
        """
        Thrown when an error occours manupulating the virtualized test 
        environment. 
        """
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class ConfigError(Exception):
        """
        Thrown with the configuration file is inaccessible or malformed. 
        """
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

