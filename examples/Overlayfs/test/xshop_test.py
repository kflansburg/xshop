import os
import subprocess

def run(H):
    H.run('target','run_exploit')

def run_exploit():
    subprocess.call(['gcc','exploit.c'])
    p = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    p.stdin.write("id;exit\n")
    if "uid=0(root)" in p.stdout.read():
        return 2
    else:
        return 0
