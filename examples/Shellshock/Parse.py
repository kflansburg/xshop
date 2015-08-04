#!/usr/bin/python2.7

import json
from xshop import colors

f = open('output.json','r')

D = json.loads(f.read())

D = D[0]


cves = []
patches = []
results = []
for i in D[0]:
	patch = i['vars']['patch']
	patches.append(patch)



for i in D:
	cve = i[0]['vars']['cve']
	cves.append(cve)
	
table = []	
for i in D:
	cs = []
	for j in i:
		cs.append(j['vuln'])
	table.append(cs)

# Print Header
print "\t",
for i in patches:
	print " %02d"%(i),

print""
for c,t in zip(cves,table):
	print "%s\t"%(c),
	for r in t:
		if r:
			print colors.colors.FAIL+" X "+colors.colors.ENDC,
		else:
			print colors.colors.OKGREEN+" O "+colors.colors.ENDC,
	print ""
