#!/usr/bin/env python3
from pathlib import Path

MASK64 = (1 << 64) - 1
OUTPUT_PATH = Path("generated_data.h")
PASSWORD = "ever heard of the critically acclaimed ltrace?"
FLAG = "dctf{7r4C1N9_c4lls_1S_v3ry_US3fUL_F0r_r3v3Rs3_3n91n33R1ng}"


def rotl64(x: int, r: int) -> int:
    return ((x << r) & MASK64) | (x >> (64 - r))


def derive_seed(parts: list[int]) -> int:
    acc = 0x6A09E667F3BCC909
    for i, p in enumerate(parts):
        acc ^= rotl64((p + i * 0x9E3779B97F4A7C15) & MASK64, (i * 11 + 7) & 63)
        acc = (acc * 0xD6E8FEB86659FD93) & MASK64
        acc ^= acc >> 27
        acc = rotl64(acc, 17)
    return acc


def keystream_byte(seed: int, nonce: int, idx: int) -> int:
    block = idx // 8
    lane = idx % 8
    shift = (lane * 13) & 63
    x = seed ^ ((nonce + block * 0x9E3779B97F4A7C15) & MASK64)
    for r in range(10):
        x ^= rotl64(x, 7)
        x = (x * 0xD6E8FEB86659FD93) & MASK64
        x ^= x >> 17
        x = (x + (0xA5A5A5A5A5A5A5A5 ^ (r * 0x123456789))) & MASK64
    return ((x >> shift) & 0xFF) ^ ((0x5A + lane * 17) & 0xFF)


def crypt(data: bytes, seed: int, nonce: int) -> bytes:
    out = bytearray(data)
    for i in range(len(out)):
        out[i] ^= keystream_byte(seed, nonce, i)
    return bytes(out)


def format_u64_array(name: str, values: list[int]) -> str:
    body = ",\n    ".join(f"0x{v:016X}ULL" for v in values)
    return (
        f"static const uint64_t {name}[{len(values)}] = {{\n"
        f"    {body}\n"
        f"}};\n"
    )


def format_u8_array(name: str, values: bytes) -> str:
    chunks = [values[i:i + 10] for i in range(0, len(values), 10)]
    rows = [", ".join(f"0x{b:02x}" for b in chunk) for chunk in chunks]
    body = ",\n    ".join(rows)
    return (
        f"static const unsigned char {name}[{len(values)}] = {{\n"
        f"    {body}\n"
        f"}};\n"
    )


def emit_header(path: Path, pass_plain: str, flag_plain: str) -> None:
    k_parts = [
        0x243F6A8885A308D3,
        0x13198A2E03707344,
        0xA4093822299F31D0,
        0x082EFA98EC4E6C89,
        0x452821E638D01377,
        0xBE5466CF34E90C6C,
    ]
    pass_nonce = 0xC0FFEE1234ABCD01
    flag_nonce = 0xBADC0FFEE0DDF00D

    seed = derive_seed(k_parts)
    enc_pass = crypt(pass_plain.encode("utf-8") + b"\0", seed, pass_nonce)
    enc_flag = crypt(flag_plain.encode("utf-8") + b"\0", seed, flag_nonce)

    content = "\n".join(
        (
            "#ifndef GENERATED_DATA_H",
            "#define GENERATED_DATA_H",
            "",
            "#include <stdint.h>",
            "",
            format_u64_array("k_parts", k_parts).rstrip(),
            "",
            "static const uint64_t pass_nonce = 0xC0FFEE1234ABCD01ULL;",
            "static const uint64_t flag_nonce = 0xBADC0FFEE0DDF00DULL;",
            "",
            format_u8_array("enc_pass", enc_pass).rstrip(),
            "",
            format_u8_array("enc_flag", enc_flag).rstrip(),
            "",
            "#endif",
            "",
        )
    )

    path.write_text(content, encoding="utf-8")


def main() -> None:
    emit_header(OUTPUT_PATH, PASSWORD, FLAG)


if __name__ == "__main__":
    main()
