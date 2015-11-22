import os
import subprocess

def run(run_function):
    run_function('target','run_exploit')

def run_exploit():
    subprocess.call(['gcc','exploit.c'])
    p = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    p.stdin.write("id;exit\n")
    output = p.stdout.read()
    print output
    if "uid=0(root)" in output:
        return 2
    else:
        return 0
