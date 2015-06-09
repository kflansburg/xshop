#
#	new
#
#		The goal of this module is to provide functions for
#		creating the directory structure and copying 
#		templates into new projects. 
#
#		Projects include Test and Build projects.
#
#		The structure for Test Project:
#
#		PROJECT_NAME
#		|- docker-compose.yml
#		|- containers
#		|	|- target
#		|	|	|- Dockerfile
#		|	|- attacker
#		|	|	|- Dockerfile
#		|- test
#		|	|- test.py
#
