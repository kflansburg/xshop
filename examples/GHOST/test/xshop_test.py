import subprocess

def run(run_function):
	run_function('target','run_exploit')

def run_exploit():
	p = subprocess.Popen(["/usr/local/build/lib/ld-linux-x86-64.so.2","--library-path","/usr/local/build/lib","./GHOST"],stdout=subprocess.PIPE)
	result = p.communicate()
	if p.returncode:
		return 1
	if result[0] == 'vulnerable\n':
		return 2
	else:
		return 0
