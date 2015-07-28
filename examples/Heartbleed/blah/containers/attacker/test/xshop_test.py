import heartbleed
from subprocess import call as sh

def run(H):
	H.run('target','show_version')
	H.run('attacker','run_exploit')

def show_version():
	sh(['lsb_release','-a'])

def run_exploit():
	return heartbleed.main()
