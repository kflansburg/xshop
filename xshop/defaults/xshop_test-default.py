#
# Define the code which runs inside the test containers. 
#
# Use the run() function to list which hooks should run in which containers
# and in what order. Simply call run() as many times as needed. 
#

def run(run):
	run('attacker','run_exploit')

def run_exploit():
	return 0
