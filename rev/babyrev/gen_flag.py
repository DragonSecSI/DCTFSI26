#!/usr/bin/env python3

import random
import re

MAGIC_A = 0xDEADC0DE
MAGIC_B = 0x42
STEP = 3
KEY_SEED = 0xC0FFEE

def main():
    flag = open("flag.txt", encoding="utf-8").read().strip()
    random.seed(KEY_SEED)
    key = random.randbytes(len(flag))

    print("%-20.20s%s" % ("Flag:", flag))
    print("%-20.20s%s" % ("Flag hex:", flag.encode().hex()))
    print("%-20.20s%s" % ("Key:", key.hex()))
    flag_enc = encrypt_flag(pt=flag, key=key)
    print("%-20.20s%s" % ("Encrypted:", flag_enc.hex()))
    flag_dec = decrypt_flag(flag_enc, key)
    print("%-20.20s%s" % ("Decrypted:", flag_dec))
    assert flag == flag_dec

    c_prog = open("main.c", encoding="utf-8").read()
    c_prog = re.sub(r'"flag"', to_c_byte_array(flag_enc), c_prog)
    c_prog = re.sub(r'"key"', to_c_byte_array(key), c_prog)
    c_prog = re.sub(r'"flag_length"', str(len(flag_enc)), c_prog)
    open("main_compile.c", "w+", encoding="utf-8").write(c_prog)

def encrypt_flag(pt: str, key: bytes) -> bytes:
    pt = pt.encode("utf-8")
    flag_enc = []

    for i in range(len(pt)):    
        flag_enc.append((((pt[i] ^ key[i]) + MAGIC_A - (i * STEP)) ^ MAGIC_B) & 0xFF)

    return bytes(flag_enc)

def decrypt_flag(ct: bytes, key: bytes) -> str:
    flag_dec = []

    for i in range(len(ct)):
        flag_dec.append(((((ct[i] ^ MAGIC_B) - MAGIC_A + (i * STEP)) & 0xFF) ^ key[i]))

    return bytes(flag_dec).decode()

def to_c_byte_array(x: bytes) -> str:
    return "{ 0x" + x.hex(',').replace(',', ', 0x') + " }"

if __name__ == "__main__":
    main()
