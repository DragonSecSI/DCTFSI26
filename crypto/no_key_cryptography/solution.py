xor = lambda a, b: bytes(x ^ y for x, y in zip(a, b))
ptx_candidates = []
with open('output.txt') as f:
    for _ in range(100):
        enc_flag = bytes.fromhex(f.readline())
        samples = []
        for _ in range(20):
            samples.append(bytes.fromhex(f.readline()))
        
        key = bytes(max(c) for c in zip(*samples))
        ptx_candidates.append(xor(key, enc_flag))
        print(ptx_candidates[-1])

from collections import Counter
print(bytes(Counter(c).most_common(1)[0][0] for c in zip(*ptx_candidates)))


