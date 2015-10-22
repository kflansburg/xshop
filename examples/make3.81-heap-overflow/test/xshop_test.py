import subprocess
import os

def run(H):
    H.run('target','run_exploit')

def run_exploit():
    os.system("ulimit -c unlimited;perl exploit.pl")
    if os.path.exists('./core'):
        return 2
    else:
        return 0
