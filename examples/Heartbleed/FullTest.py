#!/usr/bin/python2.7

from xshop import test

variables = {'version':['1.0.0r','1.0.1a','1.0.1f','1.0.1g']}

T = test.Trial(variables)

T.run()
