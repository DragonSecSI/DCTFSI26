from pwn import *

p = remote("localhost", 1337)
p.recvline()
for i in range(25):
    l = p.recvuntil(b" = ")
    l = l.strip().split(b" ")
    a, b = int(l[0]), int(l[2])
    p.sendline(str(a + b).encode())
p.interactive()
