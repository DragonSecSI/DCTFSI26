import random, time
from werkzeug.security import check_password_hash, generate_password_hash

CLOCK_SEQ: int = random.randint(0, (1 << 14) - 1)
NODE: int = random.randint(0, (1 << 48) - 1)
MOFIFIER: int = 1

def uuid1_now() -> str:
    return get_uuid1(int(time.time() * MOFIFIER), CLOCK_SEQ, NODE)

def get_uuid1(timestamp: int, clock_seq: int, node: int) -> str:
    """
    Generate a UUID v1 manually.

    :param timestamp: intervals since 1582-10-15
    :param clock_seq: 14-bit sequence number
    :param node: 48-bit node
    :return: UUID string
    """

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
