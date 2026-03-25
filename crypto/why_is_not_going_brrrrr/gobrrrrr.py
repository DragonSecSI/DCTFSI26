import os
from hashlib import shake_128
from secrets import token_bytes

FLAG = os.environ.get('FLAG', "dctf{<REDACTED>}").encode()

N = 20
assert N & 1 == 0
mask = (1 << (N*8)) - 1
q = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a63a36210000000000090563

def filter_k(k, s): return pow(k, s, q) & 0xFF
def filter_2(s): return pow(2, s, q) & 0xFF
xor = lambda a, b: bytes(x ^ y for x, y in zip(a, b))

def step(key, state):
    k = int.from_bytes(key)
    s = int.from_bytes(state)
    s <<= 8
    s &= mask
    s += filter_k(k, s)
    s <<= 8
    s &= mask
    s += filter_2(s)
    return s.to_bytes(N)        

def stream(key, state):
    while True:
        state = step(key, state)
        yield state[-2]
        yield state[-1]

key = token_bytes(N)
state = bytes.fromhex(input(f'iv: '))

print('Warming up...')
for _ in range(100): state = step(key, state)
msg = bytes.fromhex(input('msg: '))

ctx = []
for s, b in zip(stream(key, state), msg + FLAG):
    ctx.append(s ^ b)
print(f'ctx: {bytes(ctx).hex()}')

