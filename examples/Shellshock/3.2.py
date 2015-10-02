#!/usr/bin/python2.7
import json
from xshop import test

#versions = {'3.0':22,'3.1':23,'3.2':53,'4.0':44,'4.1':17,'4.2':53,'4.3':39}
version = '3.2'
patches=53

cves = ['6271','6277','6278','7169','7186','7187','LAST']

variables = {'version':[version],'patch':list(xrange(54,58)), 'cve':cves}
print "Version: "+version
T = test.Trial(variables)
T.run()
print T.results()
f = open(version+'.log','w')
json.dump(T.results(),f)
f.close()
