import sys
import random
from queue import Empty, Queue
from threading import Thread
from pathlib import Path
from time import sleep
from smartcard.scard import SCARD_E_CANCELLED
from smartcard.System import readers as get_readers
from smartcard.CardMonitoring import CardMonitor, CardObserver
import inquirer

try:
    from playsound3 import playsound
except ImportError:
    playsound = None

CARD_KEY = [0xDC, 0x7F, 0x20, 0x26, 0x13, 0x37]
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
SUCCESS_SOUND = "TADA.wav"
FAIL_SOUND = "CHORD.wav"

class AudioPlayer:
    def __init__(self):
        self.queue = Queue()
        self.worker = Thread(target=self._run, daemon=True)
        self.worker.start()

    def _run(self):
        while True:
            try:
                sound_path = self.queue.get(timeout=0.5)
            except Empty:
                continue

            try:
                playsound(str(sound_path), block=True)
            except Exception as e:
                print("Failed to play sound {}: {}".format(sound_path.name, e))
                print("\a", end="", flush=True)

    def enqueue(self, sound_path):
        self.queue.put(sound_path)


audio_player = AudioPlayer() if playsound is not None else None

def play_sound(sound_name):
    if audio_player is None:
        print("playsound is not installed. Cannot play:", sound_name)
        print("\a", end="", flush=True)
        return

    sound_path = Path(__file__).resolve().with_name(sound_name)
    if not sound_path.exists():
        print("Sound file not found:", sound_path)
        return

    audio_player.enqueue(sound_path)

def generate_flag():
    flag = "fake{flag_try_your_tag"
    # for i in range(8):
    #     flag += "{:02x}".format(random.randint(0, 255))
    flag += "}"
    return flag

def select_reader():
    readers = get_readers()
    if not readers:
        print("No smart card readers found.")
        return None

    questions = [
        inquirer.List('reader',
                      message="Select a smart card reader",
                      choices=readers)
    ]
    answer = inquirer.prompt(questions)
    selected_reader = answer['reader']
    return selected_reader

def create_apdu(ins, data = None, p1 = 0x00, p2 = 0x00, le = None):
    if data is None:
        data = []
    apdu = [0xFF, ins, p1, p2]
    if data:
        apdu.extend([len(data)] + data)
    if le is not None:
        apdu.append(le)
    return apdu

def get_uid_cmd():
    return create_apdu(0xCA, p1 = 0x00, p2 = 0x00, le = 4)

def load_key(key, reader_key = False, key_slot = 0x00, non_volatile = True):
    p1 = 0x00
    if reader_key:
        p1 |= 0x80
    if non_volatile:
        p1 |= 0x20
    return create_apdu(0x82, key, p1, key_slot)

def read_binary(address, length):
    return create_apdu(0xB0, p1 = address >> 8, p2 = address & 0xFF, le = length)

def update_binary(address, data):
    return create_apdu(0xD6, data, p1 = address >> 8, p2 = address & 0xFF)

def authenticate(address, key_type = 0x60, key_slot = 0x00):
    return create_apdu(0x86, data = [0x01, address >> 8, address & 0xFF, key_type, key_slot])

def get_uid(connection):
    response, sw1, sw2 = connection.transmit(get_uid_cmd())
    if (sw1, sw2) != (0x90, 0x00):
        print("Failed to get UID. SW1: {:02X}, SW2: {:02X}".format(sw1, sw2))
        return None
    return response

def authenticate_block(connection, block, key_type = 0x60, key_slot = 0x00):
    auth_apdu = authenticate(block, key_type = key_type, key_slot = key_slot)
    _, sw1, sw2 = connection.transmit(auth_apdu)
    if (sw1, sw2) != (0x90, 0x00):
        print("Failed to authenticate block {}. SW1: {:02X}, SW2: {:02X}".format(block, sw1, sw2))
        return False
    return True

def read_block(connection, block):
    response, sw1, sw2 = connection.transmit(read_binary(block, 16))
    if (sw1, sw2) != (0x90, 0x00):
        print("Failed to read block {}. SW1: {:02X}, SW2: {:02X}".format(block, sw1, sw2))
        return None
    return response

def write_block(connection, block, data):
    apdu = update_binary(block, data)
    _, sw1, sw2 = connection.transmit(apdu)
    if (sw1, sw2) != (0x90, 0x00):
        print("Failed to write block {}. SW1: {:02X}, SW2: {:02X}".format(block, sw1, sw2))
        return False
    return True

def read_sector(connection, sector, key_type = 0x60, key_slot = 0x00):
    start_block = sector * 4
    trailer_block = start_block + 3
    if not authenticate_block(connection, trailer_block, key_type = key_type, key_slot = key_slot):
        return False

    print("Sector {} authenticated successfully.".format(sector))
    for block in range(start_block, start_block + 4):
        response = read_block(connection, block)
        if response is None:
            return False

        block_data = " ".join("{:02X}".format(byte) for byte in response)
        print("Block {}: {}".format(block, block_data))

    return True

def generate_sector_trailer(key_a, access_bits, key_b):
    trailer = [0] * 16
    trailer[0:6] = key_a
    trailer[6:10] = access_bits
    trailer[10:16] = key_b
    return trailer

def set_sector_trailer(connection, sector, key_a, access_bits, key_b):
    trailer = generate_sector_trailer(key_a, access_bits, key_b)
    address = (sector + 1) * 4 - 1
    if not write_block(connection, address, trailer):
        return False
    print("Sector trailer set successfully for sector", sector)
    return True

def write_sector_data(connection, sector, payload):
    start_block = sector * 4
    data_blocks = 3
    capacity = data_blocks * 16
    payload_bytes = list(payload.encode("ascii"))

    if len(payload_bytes) > capacity:
        print("Payload too large for sector {}: {} > {} bytes".format(sector, len(payload_bytes), capacity))
        return False

    padded_payload = payload_bytes + [0x00] * (capacity - len(payload_bytes))
    for block_offset in range(data_blocks):
        block = start_block + block_offset
        block_data = padded_payload[block_offset * 16:(block_offset + 1) * 16]
        if not write_block(connection, block, block_data):
            return False
        print("Wrote block {}.".format(block))

    return True

def configure_sector_one(connection, flag):
    sector = 1
    trailer_block = sector * 4 + 3
    if not authenticate_block(connection, trailer_block, key_slot = 0x00):
        print("Failed to authenticate sector 1 with the original key.")
        if not authenticate_block(connection, trailer_block, key_slot = 0x01):
            print("Failed to authenticate sector 1 with the custom key.")
            return False

    trailer = read_block(connection, trailer_block)
    if trailer is None:
        print("Failed to read sector 1 trailer.")
        return False

    access_bits = trailer[6:10]
    if not write_sector_data(connection, sector, flag):
        print("Failed to write flag to sector 1.")
        return False

    if not set_sector_trailer(connection, sector, CARD_KEY, access_bits, CARD_KEY):
        print("Failed to update sector 1 trailer.")
        return False

    print("Sector 1 configured with custom keys and flag payload.")
    return True

def load_keys(connection):
    # load default key to slot 0
    load_default_apdu = load_key(DEFAULT_KEY, key_slot=0x00)
    _, sw1, sw2 = connection.transmit(load_default_apdu)
    if (sw1, sw2) != (0x90, 0x00):
        print("Failed to load default key. SW1: {:02X}, SW2: {:02X}".format(sw1, sw2))
        return False
    print("Default key loaded successfully.")
    # load custom key to slot 1
    load_custom_apdu = load_key(CARD_KEY, key_slot=0x01)
    _, sw1, sw2 = connection.transmit(load_custom_apdu)
    if (sw1, sw2) != (0x90, 0x00):
        print("Failed to load custom key. SW1: {:02X}, SW2: {:02X}".format(sw1, sw2))
        return False
    print("Custom key loaded successfully.")
    return True

class ReaderSession:
    def __init__(self):
        self.key_loaded = False

    def ensure_keys_loaded(self, connection):
        if self.key_loaded:
            return True

        if not load_keys(connection):
            print("Failed to load keys. Cannot proceed.")
            return False

        self.key_loaded = True
        return True

def process_card(connection, session):
    connection.connect()
    if not session.ensure_keys_loaded(connection):
        return False
    flag = generate_flag()
    print("Writing flag to sector 1:", flag)
    if not configure_sector_one(connection, flag):
        print("Failed to configure sector 1.")
        return False
    # append flag to flag.txt for verification
    with open("flag.txt", "a") as f:
        f.write(f"{flag}\n")

    return True

class ReaderCardObserver(CardObserver):
    def __init__(self, target_reader):
        super().__init__()
        self.target_reader = target_reader
        self.reader_name = str(target_reader)
        self.session = ReaderSession()

    def _is_target_reader(self, card):
        return str(card.reader) == self.reader_name

    def update(self, observable, handlers):
        added_cards, removed_cards = handlers

        for card in added_cards:
            if not self._is_target_reader(card):
                continue

            print("Card detected in reader:", self.reader_name)
            try:
                ok = process_card(card.createConnection(), self.session)
                play_sound(SUCCESS_SOUND if ok else FAIL_SOUND)
            except Exception as e:
                print("Error while processing card:", e)
                play_sound(FAIL_SOUND)

        for card in removed_cards:
            if self._is_target_reader(card):
                print("Card removed from reader:", self.reader_name)

def main():
    reader = select_reader()
    if not reader:
        raise ValueError("No reader selected.")

    monitor = CardMonitor()
    observer = ReaderCardObserver(reader)
    monitor.addObserver(observer)

    print("Monitoring reader events for:", reader)
    print("Insert/remove a card. Press Ctrl+C to exit.")

    try:
        while True:
            # Keep process alive while CardMonitor callbacks handle events.
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")
    except Exception as e:
        if getattr(e, "hresult", None) == SCARD_E_CANCELLED:
            print("Card monitoring cancelled.")
            sys.exit(0)
        raise
    finally:
        monitor.deleteObserver(observer)

if __name__ == "__main__":
    main()
