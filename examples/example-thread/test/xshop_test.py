#
# Define the code which runs inside the test containers.
#
# Use the run() function to list which hooks should run in which containers
# and in what order. Simply call H.run() as many times as needed.
#
# Hooks can be any function in this file.
#
from subprocess import call as sh
import os

def run(H):
	H.run('attacker','run_exploit')

def run_exploit():
    try:
        cflag =os.environ['cflag']
    except KeyError:
        cflag=''

    if sh(['clang','tsan_example.c','-pthread',cflag]):
        return 1

    ret = sh(['./a.out'])
    if ret==0:
        return 2
    else:
        return 0
