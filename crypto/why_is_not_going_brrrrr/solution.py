import pwn
from secrets import token_bytes

pwn.context.log_level = "error"

N = 20
assert N & 1 == 0
mask = (1 << (N*8)) - 1
q = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a63a36210000000000090563

def filter_k(k, s): return pow(k, s, q) & 0xFF
def filter_2(s): return pow(2, s, q) & 0xFF

def solve(first):
    options = []
    for second in range(256):
        s = int.from_bytes(bytes([second, first] * (N//2))[1:] + b'\0')
        if filter_2(s) == second:
            options.append(second)
    return options

def step(state):
    with pwn.remote('localhost', 1337) as con:
        con.recvuntil(b'iv: ')
        con.sendline(state.hex().encode())
        con.recvuntil(b'msg: ')
        con.sendline(bytes(N).hex().encode())
        con.recvuntil(b'ctx: ')
        ct = bytes.fromhex(con.recvline().strip().decode())
    return ct

# lut = { first:second_ for first in range(256) if (second_ := solve(first)) }
# print(f'{lut = }')

# for i in range(256):
#     for first, second_ in lut.items():
#         for second in second_:
#             good_state = bytes([first, second] * (N//2))
#             ct = step(good_state)
#             if good_state == ct[:N]:
#                 print(f'\n{good_state.hex() = }')
#                 print(f"{pwn.xor(ct, good_state*5, cut='left')[N:] = }")
#                 break

good_state = None
for first in range(256):
    if (second := solve(first)):
        good_state = bytes([first, second[0]] * (N//2))
        break
assert good_state
print(f'good_state: {good_state.hex()}')

for i in range(10000):
    # good_state = b'tTtTtTtTtTtTtTtTtTtT'
    ct = step(good_state)
    print(i, end=' ', flush=True)
    if good_state == ct[:N]:
        print(f'\n{good_state.hex() = }')
        print(f"{pwn.xor(ct, good_state*5, cut='left')[N:] = }")
        break

