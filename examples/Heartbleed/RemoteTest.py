#!/usr/bin/python2.7



from xshop import test

variables = {"AWS Vulnerable":"52.20.169.32","Google":"74.125.21.102"}


for k in variables.keys():
    v = variables[k]
    T = test.TestCase({'host':k},target=v)
    T.run()
