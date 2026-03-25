from secrets import token_bytes, randbelow

FLAG = b'ncQUTkDWOQcdT6xRxrwxqLrUWOlaSr'
xor = lambda a, b: bytes(x ^ y for x, y in zip(a, b))

with open('output.txt', 'w') as f:
    for _ in range(100):
        z = token_bytes(len(FLAG))
        f.write(xor(FLAG, z).hex() + '\n')
        for _ in range(20):
            f.write(bytes(randbelow(b+1) for b in z).hex() + '\n')
