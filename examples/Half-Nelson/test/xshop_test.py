import os
import subprocess

def run(H):
    H.run('target','run_exploit')

def run_exploit():
    subprocess.call(['gcc','half-nelson.c', '-lrt'])
    p = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE)
    if "launching root shell!" in p.stdout.read():
        return 2
    else:
        return 0
