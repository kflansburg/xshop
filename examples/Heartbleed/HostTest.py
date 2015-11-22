#!/usr/bin/python2.7
from xshop import test

T = test.TestCase({},target='image:host_image:latest')
T.run()
print T.results
