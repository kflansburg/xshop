#
#	fileselect
#
#		The goal of this module is to provide logic so that the
#		program can select which user configuration to use for
#		a particular build. The user creates a default folder
#		(debian in this example), and can override this default
#		for edge cases. This is done by adding a second folder
#		with qualifiers, separated by '_', such as debian_i386.
#		In general, behavior is much like CSS where the most
#		specific rule has precedent, here order is irrelevant.
#		The program will always select the folder with the most
#		qualifiers, all of which must match the build case.
#		In the event that two folders have the same number of
#		qualifiers, the tie will be broken by looking at the
#		relative importance of the qualifiers provided. The
#		order of importance is given as:
#
#			Architecture > Version > Release > Distribution
#
#		A 'X' can be used as a wildcard, i.e. '0.9.X' will match
#		'0.9.1c'. Additionally, '-' will match both '-' and '_'.
#

import os
import re

#
# 	Returns a list of files in `path` that have the correct
#	format: root(_qual)*
#
def list_files(path, root):
	files = os.listdir(path)
	regex = re.compile("^"+root+"(_[^\n_]+)*$")
	files = filter(lambda x: regex.match(x),files)
	return files

#
#	Looks for folders in `path` whose default name is `root`.
# 	Filters to make sure that all qualifiers match the build
# 	scenario outlined in dictionary `d`. Then selects the most
#	specific folder name.
#
def select(path, root, d):
	pass
	# Generate a list of files with matching root

	# Update with parsed qualifiers

	# Check that all qualifiers match and detect rank

	# Filter for files that entirely match

	# Filter for max length

	# If remaining list is longer than 1, filter by max rank
