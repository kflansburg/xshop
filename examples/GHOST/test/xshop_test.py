import os
import subprocess
def run_exploit():
        if os.environ['CONTAINER_NAME']=='target':
                p = subprocess.Popen(["/usr/local/build/lib/ld-linux-x86-64.so.2","--library-path", "/usr/local/build/lib","./GHOST"],stdout=subprocess.PIPE)
                result = p.communicate()
                if result[0] == 'vulnerable\n':
                        return 2
                else:
                        return 0
        else:
                return 0
