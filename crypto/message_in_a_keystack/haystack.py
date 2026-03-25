
from secrets import randbelow

p = 9223372036854777341
q = 9223372036854777343

def auth_encrypt(p, msg, enc_keys, mac_key):
    assert msg < p
    ctx = (sum(enc_keys) + msg) % p
    mac = mac_key * ctx % p
    return ctx, mac

M = 5
N = 20

everything = []

msgs = [randbelow(q) for _ in range(M)]
FLAG = msgs[-1]
with open('flag.txt', 'w') as f:
    f.write(f'dctf{{{FLAG}}}')

for msg in msgs:
    for i in range(N):
        enc_keys = [randbelow(p) for _ in range(2)]
        mac_key = randbelow(p)
        c = auth_encrypt([p, q][msg & 1], msg, enc_keys, mac_key)
        everything.extend(enc_keys)
        everything.append(mac_key)
        everything.extend(c)

with open('haystack.txt', 'w') as f:
    for x in sorted(everything):
        f.write(f'{x:020x}\n')
