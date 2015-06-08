#
#	template
#
#		This module provides functions for applying
#		templating to files and folders. The general
#		behavior is for a dictionary of substitutions
# 		to be provided where <%= variable %> is
#		replaced by the value of variable in every
# 		appearance in the file. The function reports
#		if any template elements remain in the file.
#

#
#	Replaces substitutions within a file. Destructive
#
def template_file(path,d):
	pass

#
#	Traverses a folder and runs template_file on each
#	file found. Destructive
#
def template_folder(path,d):
	pass

#
#	Accepts a file or folder `path`, copies it to
#	`output`, and then applies templating in place.
#
def template_and_copy(path,output,d):
	pass
