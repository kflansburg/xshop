import heartbleed
from subprocess import call as sh
import os

def run(H):
	H.run('attacker','run_exploit')

def run_exploit():
        print os.environ['container']
	return heartbleed.main()
