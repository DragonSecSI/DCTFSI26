from pwn import *

elf = ELF("game-linux-x86_64")
data = bytearray(elf.data)

data[3698 - 1] = 0x90
data[3699 - 1] = 0x90

with open("game-linux-x86_64_patched2", "wb") as f:
    f.write(data)