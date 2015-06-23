#
#	config
#
#		Module that persists project information in
#		a file named .config in the root of the 
#		project directory
#

import os
import yaml

#
#	Checks if there is a .config file in the working 
#	diractory (implying that this is a project folder)
#
def check():
	if os.path.isfile("config.yaml"):
		return True
	else:
		return False

#
#	Object which represents a config file and allows
#	reading and writing files
#
class Config:
	#
	#	Checks if a config already exists and if
	#	not creates a new one.
	#
	def __init__(self):
		self.path='config.yaml'
		if os.path.isfile(self.path):
			self.load_config()
		else:
			self.generate_new_config()
	
	#
	#	Initializes config as empty dict and saves
	#	
	def generate_new_config(self):
		self.config={}
		self.persist()

	#
	#	Saves config dict as json dump
	# 
	def persist(self):
		f = open(self.path,'w')
		f.write(yaml.dump(self.config))
		f.close()	

	#
	#	Loads json from file into config dict
	#
	def load_config(self):
		f = open(self.path, 'r')
		self.config = yaml.load(f.read())
		f.close()
		
	#
	#	Returns the value of a given key
	#
	def get(self,key):
		return self.config[key]

	#
	#	Sets the value of a key and persists
	#
	def put(self,key,value):
		self.config[key]=value
		self.persist()

		
