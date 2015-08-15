import heartbleed
import subprocess
import os
import time

def run(H):
    H.run('target','start_server')
    time.sleep(1)
    H.run('attacker','run_exploit')

def start_server():
    print os.environ
    subprocess.Popen(["openssl"
        " s_server"
        " -key"
        " server.key"
        " -cert"
        " server.cert5"
        " -accept"
        " 443"
        " -www"], 
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    return 0


def run_exploit():
    return heartbleed.main()
