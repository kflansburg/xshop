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
    p = Popen(['./CFI'], shell=True, stdout=PIPE)
    os.system("./CFI")
    print "I am running run_Explotit!"
    try:
        r = p.stdout.read(4)
        print "="*10 + "\nI_LOVE_IU:" +r
        if (r == "EVIL"):
            return 2
    except:
        return 0
