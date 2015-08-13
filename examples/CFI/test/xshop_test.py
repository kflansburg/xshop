#
# Define the code which runs inside the test containers.
#
# Use the run() function to list which hooks should run in which containers
# and in what order. Simply call H.run() as many times as needed.
#
# Hooks can be any function in this file.
#
from subprocess import call as sh
from subprocess import *
import os

def run(H):
	H.run('target','run_exploit')

def run_exploit():
    os.system("ls -als")
    os.system("clang -v")
    try:
        cflag =os.environ['cxxflags']
    except KeyError:
        cflag=''

    if sh(['make','CXX=clang++','CXXFLAGS=%s' % cflag]):
        return 1

    p = Popen(['./CFI'], shell=True, stdout=PIPE)
    try:
        if (p.stdout.read(4) == "EVIL"):
            return 2
    except:
        return 0
