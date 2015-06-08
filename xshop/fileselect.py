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
import logging

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
# 	This function takes a qualifier and returns whether it 
# 	matches the attribute. This includes considering 'X' 
# 	to be a wildcard and '-' and '_' to be equal.
#
def match(qual,attr):
	# Escape input string, then substitute special chars with 
	# regex
	qual = re.escape(qual)
	qual = "^"+qual.replace('X','.+').replace('\-','[-_]') + "$"
	return re.compile(qual).match(attr)

#
# 	Takes a filename string and dictionary of build scenario. 
# 	Checks that all qualifiers match the scenario, otherwise
# 	return false. If all match, also computes highest rank of 
# 	qualifier type (ARCH vs DIST, etc.).
#
def parse_qualifiers(filename,d):
	RANKS = ['DIST','RELEASE','VERSION','ARCH']
	
	RANK = -1
	# Split qualifiers, ignoring root
	quals = filename.split('_')[1:]

	# For each qualifier, check what it matches
	for q in quals:
		m = False
		for k in d.keys():
			if match(q,d[k]):
				# Match found, update rank if neccessary
				m=True
				if RANKS.index(k)>RANK:
					RANK = RANKS.index(k)
					break
		if not m:
			# If no match was found, reject file
			return False

	return {'filename':filename,'len':len(quals), 'rank': RANK}


#
#	Looks for folders in `path` whose default name is `root`.
# 	Filters to make sure that all qualifiers match the build
# 	scenario outlined in dictionary `d`. Then selects the most
#	specific folder name.
#
def select(path, root, d):
	# Generate a list of files with matching root
	files = list_files(path,root)

	# Update with parsed 
	files = map(lambda x: parse_qualifiers(x, d), files)

	# Filter for files that entirely match

	# Filter for max length

	# If remaining list is longer than 1, filter by max rank
