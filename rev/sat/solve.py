#!/usr/bin/env python3
import argparse
from pathlib import Path

from z3 import BitVec, BitVecVal, Or, RotateLeft, Solver, UGE, ULE, sat

FLAG = "dctf{Ju5t_s0lv3_The_Con5tr4ints!}"


def u8(v):
    return v & 0xFF


def rol8(v, r):
    r &= 7
    return u8((v << r) | (v >> (8 - r)))


def derive_constraints(flag):
    b = [ord(c) for c in flag]
    n = len(b)
    if n < 8:
        raise ValueError("FLAG must be at least 8 chars")

    prefix_len = flag.index("{") + 1 if "{" in flag else max(1, min(7, n - 1))

    c1 = [u8(7 * b[i] + 11 * b[i + 1] + 13 * b[i + 2] + 17 * b[i + 3] + 19 * i) for i in range(n - 3)]
    c2 = [u8(rol8(b[i], 1) ^ rol8(b[i + 1], 2) ^ rol8(b[i + 2], 3) ^ b[i + 3] ^ u8(b[i + 4] + 7 * i)) for i in range(n - 4)]

    c3 = []
    for i in range(n):
        j = (i * 7 + 3) % n
        k = (i * 11 + 5) % n
        c3.append(u8((b[i] + b[j]) ^ u8(3 * b[k] + i)))

    c4 = []
    for i in range(n - 5):
        c4.append(
            u8(
                rol8(b[i], (i % 7) + 1)
                + (b[i + 1] ^ b[i + 3])
                + 3 * b[i + 2]
                + 5 * b[i + 4]
                + 7 * b[i + 5]
                + 13 * i
            )
        )

    c5 = []
    for i in range(n):
        j = (i * 5 + 1) % n
        k = (i * 9 + 2) % n
        t = (i + 3) % n
        p = (i + 4) % n
        c5.append(u8((b[i] & b[j]) ^ (b[k] | b[t]) ^ u8(~b[p])))

    g1 = u8(sum(((17 * i + 3) & 0xFF) * b[i] for i in range(n)))
    g2 = 0
    for i in range(n):
        g2 ^= rol8(b[i], (i % 5) + 1)

    return {
        "flag_len": n,
        "prefix_bytes": [ord(c) for c in flag[:prefix_len]],
        "last_byte": ord(flag[-1]),
        "c1": c1,
        "c2": c2,
        "c3": c3,
        "c4": c4,
        "c5": c5,
        "g1": g1,
        "g2": u8(g2),
    }


def build_solver(cons):
    n = cons["flag_len"]
    xs = [BitVec(f"x{i}", 8) for i in range(n)]
    s = Solver()

    for i, byte in enumerate(cons["prefix_bytes"]):
        s.add(xs[i] == byte)
    s.add(xs[n - 1] == cons["last_byte"])

    # Keep unknown bytes printable to avoid weird control-char solutions.
    for i in range(len(cons["prefix_bytes"]), n - 1):
        s.add(UGE(xs[i], BitVecVal(0x20, 8)))
        s.add(ULE(xs[i], BitVecVal(0x7E, 8)))

    for i, val in enumerate(cons["c1"]):
        s.add(7 * xs[i] + 11 * xs[i + 1] + 13 * xs[i + 2] + 17 * xs[i + 3] + BitVecVal(19 * i, 8) == BitVecVal(val, 8))

    for i, val in enumerate(cons["c2"]):
        s.add(
            RotateLeft(xs[i], 1)
            ^ RotateLeft(xs[i + 1], 2)
            ^ RotateLeft(xs[i + 2], 3)
            ^ xs[i + 3]
            ^ (xs[i + 4] + BitVecVal(7 * i, 8))
            == BitVecVal(val, 8)
        )

    for i, val in enumerate(cons["c3"]):
        j = (i * 7 + 3) % n
        k = (i * 11 + 5) % n
        s.add(((xs[i] + xs[j]) ^ (3 * xs[k] + BitVecVal(i, 8))) == BitVecVal(val, 8))

    for i, val in enumerate(cons["c4"]):
        rot = (i % 7) + 1
        s.add(
            RotateLeft(xs[i], rot)
            + (xs[i + 1] ^ xs[i + 3])
            + 3 * xs[i + 2]
            + 5 * xs[i + 4]
            + 7 * xs[i + 5]
            + BitVecVal(13 * i, 8)
            == BitVecVal(val, 8)
        )

    for i, val in enumerate(cons["c5"]):
        j = (i * 5 + 1) % n
        k = (i * 9 + 2) % n
        t = (i + 3) % n
        p = (i + 4) % n
        s.add(((xs[i] & xs[j]) ^ (xs[k] | xs[t]) ^ (~xs[p])) == BitVecVal(val, 8))

    acc1 = BitVecVal(0, 8)
    for i in range(n):
        acc1 = acc1 + BitVecVal((17 * i + 3) & 0xFF, 8) * xs[i]
    s.add(acc1 == BitVecVal(cons["g1"], 8))

    acc2 = BitVecVal(0, 8)
    for i in range(n):
        acc2 = acc2 ^ RotateLeft(xs[i], (i % 5) + 1)
    s.add(acc2 == BitVecVal(cons["g2"], 8))

    return s, xs


def solve_flag(cons):
    s, xs = build_solver(cons)
    if s.check() != sat:
        raise RuntimeError("SAT instance is UNSAT")
    m = s.model()
    return "".join(chr(m[x].as_long()) for x in xs)


def verify_unique_with_z3(cons, candidate):
    if len(candidate) != cons["flag_len"]:
        return False, "wrong length"

    s, xs = build_solver(cons)
    for i, ch in enumerate(candidate):
        s.add(xs[i] == ord(ch))

    if s.check() != sat:
        return False, "candidate violates SAT constraints"

    m = s.model()
    s.add(Or([x != BitVecVal(m[x].as_long(), 8) for x in xs]))
    if s.check() == sat:
        return False, "multiple satisfying candidates exist"

    return True, "candidate is SAT and unique"


def format_array(name, values, width=12):
    chunks = []
    for i in range(0, len(values), width):
        chunks.append("    " + ", ".join(str(v) for v in values[i : i + width]))
    body = ",\n".join(chunks)
    return f"static const uint8_t {name}[{len(values)}] = {{\n{body}\n}};"


def emit_header(cons):
    prefix = ", ".join(str(v) for v in cons["prefix_bytes"])
    lines = [
        "#ifndef SAT_DATA_H",
        "#define SAT_DATA_H",
        "",
        "#include <stdint.h>",
        "",
        f"#define FLAG_LEN {cons['flag_len']}",
        f"#define PREFIX_LEN {len(cons['prefix_bytes'])}",
        f"#define C1_LEN {len(cons['c1'])}",
        f"#define C2_LEN {len(cons['c2'])}",
        f"#define C3_LEN {len(cons['c3'])}",
        f"#define C4_LEN {len(cons['c4'])}",
        f"#define C5_LEN {len(cons['c5'])}",
        "",
        f"static const uint8_t KNOWN_PREFIX[PREFIX_LEN] = {{{prefix}}};",
        f"static const uint8_t LAST_BYTE = {cons['last_byte']};",
        format_array("C1", cons["c1"]),
        format_array("C2", cons["c2"]),
        format_array("C3", cons["c3"]),
        format_array("C4", cons["c4"]),
        format_array("C5", cons["c5"]),
        f"static const uint8_t G1 = {cons['g1']};",
        f"static const uint8_t G2 = {cons['g2']};",
        "",
        "#endif",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate and solve a SAT CTF challenge.")
    parser.add_argument("--emit-header", action="store_true", help="Emit generated sat_data.h constants")
    parser.add_argument("--output", default="sat_data.h", help="Output header path")
    parser.add_argument("--solve", action="store_true", help="Recover and verify flag with Z3")
    args = parser.parse_args()

    cons = derive_constraints(FLAG)

    if args.emit_header:
        out = Path(args.output)
        out.write_text(emit_header(cons), encoding="utf-8")
        print(f"wrote SAT data header to {out}")

    if args.solve or not args.emit_header:
        recovered = solve_flag(cons)
        ok, msg = verify_unique_with_z3(cons, recovered)
        print(f"recovered flag: {recovered}")
        print(f"verification: {msg}")
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
