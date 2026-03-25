from secrets import randbelow
from Crypto.Util.number import getPrime
from base64 import b64encode, b64decode
import os

FLAG = os.environ.get('FLAG', 'dctf{<REDACTED>}')
NUM_REGISTERS = 10
MAX_STACK_SIZE = 100
MAX_PROGRAM_LENGTH = 32
MAX_ITER = 5000

A = [0 for _ in range(NUM_REGISTERS)]
STACK = [0 for _ in range(MAX_STACK_SIZE)]
IP = 0
SP = 0
CTR = MAX_ITER

OPCODES = ['HALT', 'DEBUG', 'NOP', 'SET', 'IPC',
           'MOV', 'SWP',
           'ADD', 'SUB', 'MUL', 'MOD', 'DIV', 'NEG',
           'PUSH', 'POP', 'PEEK',
           'JMP', 'JEZ', 'JNZ', 'JGZ', 'JLZ', 'JRA']

def assemble(program : str):
    address = 0
    labels = {}
    lines = program.split('\n')
    instructions = []
    for line in lines:
        if '#' in line: line = line[:line.index('#')].strip()
        line = line.strip()
        if line == '': continue
        if line.endswith(':'):
            line = line[:-1]
            assert line not in labels
            assert line.isalnum()
            labels[line] = address
            continue

        instruction = tuple(line.split(' '))
        assert instruction[0] in OPCODES
        instructions.append(instruction)
        address += 1
    for instruction in instructions:
        match instruction:
            case ('JMP', label) | ('JEZ', label) | ('JNZ', label) | ('JGZ', label) | ('JLZ', label):
                assert label in labels
                idx = instructions.index(instruction)
                instructions[idx] = (instruction[0], str(labels[label]))

    assert len(instructions) <= MAX_PROGRAM_LENGTH
    return instructions


def execute(opcode):
    global A
    global STACK
    global IP
    global CTR
    global SP
    # print(f'EXECUTE: {opcode}\nA={A}\nIP={IP}\nSTACK={STACK}\nSP={SP} CTR={CTR}')

    LIMIT = 1 << (512)
    def reg(x):
        if x > LIMIT:
            return x % LIMIT
        if x < -LIMIT:
            x = -((-x) % LIMIT)
        return x

    match opcode:
        case ('HALT', ): CTR = 0
        case ('DEBUG', ):
            print(f'[DEBUG] IP={IP} SP={SP}')
            for i in range(NUM_REGISTERS):
                print(f'[DEBUG] a{i}={A[i]}')
            for i in range(SP + 1):
                print(f'[DEBUG] s{i}={STACK[i]} {"<-" if i == SP else ""}')
        case ('NOP', ): pass
        case ('SET', value, dest): A[int(dest)] = reg(int(value))
        case ('IPC', dest): A[int(dest)] = IP
        case ('MOV', src, dest): A[int(dest)] = A[int(src)]
        case ('SWP', dest1, dest2): A[int(dest1)], A[int(dest2)] = A[int(dest2)], A[int(dest1)]
        case ('ADD', src1, src2, dest): A[int(dest)] = reg(A[int(src1)] + A[int(src2)])
        case ('SUB', src1, src2, dest): A[int(dest)] = reg(A[int(src1)] - A[int(src2)])
        case ('MUL', src1, src2, dest): A[int(dest)] = reg(A[int(src1)] * A[int(src2)])
        case ('DIV', src1, src2, dest): A[int(dest)] = reg(A[int(src1)] // A[int(src2)])
        case ('MOD', src1, src2, dest): A[int(dest)] = reg(A[int(src1)] % A[int(src2)])
        case ('NEG', src1, dest): A[int(dest)] = reg(-A[int(src1)])
        case ('PUSH', src): SP = (SP + 1) % len(STACK); STACK[SP] = A[int(src)]
        case ('POP', dest): A[int(dest)] = STACK[SP]; SP = (SP - 1) % len(STACK)
        case ('PEEK', dest): A[int(dest)] = STACK[SP]
        case ('JMP', addr): IP = int(addr) - 1
        case ('JEZ', addr):
            if A[0] == 0: IP = int(addr) - 1
        case ('JNZ', addr):
            if A[0] != 0: IP = int(addr) - 1
        case ('JGZ', addr):
            if A[0] > 0: IP = int(addr) - 1
        case ('JLZ', addr):
            if A[0] < 0: IP = int(addr) - 1
        case ('JRA'): IP = A[0] - 1
        case _: assert False, f'Invalid opcode: {opcode}'

ins = assemble(b64decode(input()).decode())
p = getPrime(256)
q = getPrime(256)
n = p * q
e = (1 << 521) - 1
dp = pow(e, -1, p-1)
dq = pow(e, -1, q-1)
f = pow(p, -1, q)
m = randbelow(n)

STACK[0] = f
STACK[1] = p
STACK[2] = dp
STACK[3] = q
STACK[4] = dq
STACK[5] = m
SP = 5

CTR = MAX_ITER
while CTR > 0 and IP < len(ins):
    execute(ins[IP])
    IP = (IP + 1) % len(ins)
    CTR -= 1
assert STACK[0] == pow(m, pow(e, -1, (p-1)*(q-1)), n)
print(FLAG)
