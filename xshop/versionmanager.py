#
#	version
#	
#		Module provides functions for detecting
#		versions available for build/test
#

import os
import re

#
#	Finds all tarballs of form [library]-[version].tar.{gz,xz}
#
def detect_source(library,path):
	reg = re.compile("^"+library+"-(.+).tar.[gx]z$")
	result = []
	for f in os.listdir(path):
		m = reg.match(f)
		if m:
			result.append(m.groups(1)[0])
	return result
			
