import os
import subprocess

def run(H):
    H.run('target','run_exploit')

def run_exploit():
    subprocess.call(['gcc','full-nelson.c'])
    p = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE)
    if "Got root!" in p.stdout.read():
        return 2
    else:
        return 0
