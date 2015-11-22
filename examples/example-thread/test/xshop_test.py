from subprocess import call as sh
import os

def run(run_function):
	run_function('target','run_exploit')

def run_exploit():
    print "Running Example"
    ret = sh(['/home/a.out'])
    print "Return Code: %d"%(ret,)
    if ret==0:
        return 2
    else:
        return 0
