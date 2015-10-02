#
# Define the code which runs inside the test containers. 
#
# Use the run() function to list which hooks should run in which containers
# and in what order. Simply call H.run() as many times as needed. 
#
# Hooks can be any function in this file. 
#
import exploit
def run(H):
	H.run('target','run_exploit')

def run_exploit():
    return exploit.run()

#if __name__ == '__main__':
#    print "Result : %d" % run_exploit()
