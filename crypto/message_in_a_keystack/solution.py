from tqdm import tqdm
from collections import Counter

p = 9223372036854777341
q = 9223372036854777343

def auth_encrypt(p, msg, enc_key, mac_key):
    assert msg < p
    ctx = (enc_key + msg) % p
    mac = mac_key * ctx % p
    return ctx, mac

keys = []
with open('haystack.txt') as f:
    for line in f:
        keys.append(int(line, 16))

print(len(keys))

for r in [p, q]:
    auth_t = []
    for i in tqdm(range(len(keys))):
        for j in range(i+1, len(keys)):
            for k in range(j+1, len(keys)):
                if keys[i] == keys[j] * keys[k] % r:
                    auth_t.append((keys[i], keys[j], keys[k]))
                elif keys[j] == keys[i] * keys[k] % r:
                    auth_t.append((keys[j], keys[i], keys[k]))
                elif keys[k] == keys[i] * keys[j] % r:
                    auth_t.append((keys[k], keys[i], keys[j]))

    print(len(auth_t))
    actual_keys = list(set(keys) - set(x for t in auth_t for x in t))
    print(len(actual_keys))

    msg_candidates = []
    for t in auth_t:
        for ctx in t[1:]:
            for key_i in range(len(actual_keys)):
                for key_j in range(key_i+1, len(actual_keys)):
                    msg_candidates.append((ctx - actual_keys[key_i] - actual_keys[key_j]) % r)

    print([(v, c) for v, c in Counter(msg_candidates).most_common() if c > 1])