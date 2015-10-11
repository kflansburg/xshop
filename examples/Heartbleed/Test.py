#!/usr/bin/python2.7

from xshop import test

T = test.TestCase({'version':'1.0.1a'})

T.run()

print T.results
