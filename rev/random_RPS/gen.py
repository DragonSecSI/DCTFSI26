FLAG = 'dctf{1_H473_m47H3m471cs_4nD_crYp709R4pHY}'
from secrets import token_bytes
l = list(token_bytes(32))
pt = [ord(x)*31**i % 256 for i, x in enumerate(FLAG)]
ct = [pt[0]]
for c in pt:
    ct.append((l[ct[-1] & 0x1f] + c) & 0xff)
def decrypt(l, ct):
    pt = []
    for i in range(1, len(ct)):
        prev_value = ct[i - 1]
        current_value = ct[i]
        c = (current_value - l[prev_value & 0x1f]) & 0xff
        pt.append(c)
    return [chr(x*223**i % 256) for i, x in enumerate(pt)]
print(f'const unsigned char lookupTable[32] = {{ {", ".join(str(x) for x in l)} }};')
print(f'const unsigned char encryptedMessage[] = {{ {", ".join(str(x) for x in ct)} }};')
assert FLAG == ''.join(decrypt(l, ct))
