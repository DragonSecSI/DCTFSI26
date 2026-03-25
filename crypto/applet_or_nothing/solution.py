program_sgn = """
POP 7     # a7 = m
start:
POP 1     # a1 = dq (second time is dp)
POP 2     # a2 = q  (second time is p)
MOD 7 2 4 # a4 = mp (second time is mq)
# a1 exponent, a2 modulus, a3 result, a4 base, a5 constant 2
SET 2 5
SET 1 3
loop:
    MOV 1 0
    JEZ end
    MOD 0 5 0
    JNZ mult
    JMP sqr
mult:
    MUL 4 3 3
    MOD 3 2 3
sqr:
    MUL 4 4 4
    MOD 4 2 4
    DIV 1 5 1
    JMP loop
end:
    MOV 9 0
    JNZ finish
    MOV 3 8     # a8 = sq
    MOV 2 9     # a9 = q
    JMP start
finish:
POP 7     # a7 = p^-1 mod q
SUB 8 3 0 # a0 = (sq - sp)
MUL 0 7 0 # a0 = (sq - sp) * (p^-1 mod q)
MOD 0 9 0 # a0 = (sq - sp) * (p^-1 mod q) mod q
MUL 0 2 0 # a0 = ((sq - sp) * (p^-1 mod q) mod q) * p
ADD 0 3 0 # a0 = ((sq - sp) * (p^-1 mod q) mod q) * p + sp
PUSH 0
HALT
"""

from base64 import b64encode
print(b64encode('\n'.join(line[:line.index('#')].strip() if '#' in line else line for line in program_sgn.split('\n')).encode()).decode())
# ClBPUCA3CnN0YXJ0OgpQT1AgMQpQT1AgMgpNT0QgNyAyIDQKClNFVCAyIDUKU0VUIDEgMwpsb29wOgogICAgTU9WIDEgMAogICAgSkVaIGVuZAogICAgTU9EIDAgNSAwCiAgICBKTlogbXVsdAogICAgSk1QIHNxcgptdWx0OgogICAgTVVMIDQgMyAzCiAgICBNT0QgMyAyIDMKc3FyOgogICAgTVVMIDQgNCA0CiAgICBNT0QgNCAyIDQKICAgIERJViAxIDUgMQogICAgSk1QIGxvb3AKZW5kOgogICAgTU9WIDkgMAogICAgSk5aIGZpbmlzaApNT1YgMyA4Ck1PViAyIDkKICAgIEpNUCBzdGFydApmaW5pc2g6ClBPUCA3ClNVQiA4IDMgMApNVUwgMCA3IDAKTU9EIDAgOSAwCk1VTCAwIDIgMApBREQgMCAzIDAKUFVTSCAwCkhBTFQK
