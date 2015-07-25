import heartbleed

def run(H):
	H.run('attacker','run_exploit')


def run_exploit():
	return heartbleed.main()
