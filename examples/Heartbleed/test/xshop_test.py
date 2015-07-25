import os
import heartbleed
def run_exploit():
	print os.environ['CONTAINER_NAME']	
	if os.environ['CONTAINER_NAME']=='attacker':
		return heartbleed.main()
	return 0
