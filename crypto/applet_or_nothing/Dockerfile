FROM python:3.12-slim
WORKDIR /app

RUN apt-get -y update && \
    apt-get install -y socat coreutils && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip && \
    pip install pycryptodome

COPY sim.py /app

RUN chmod 555 sim.py

CMD ["socat", "-T", "10", "TCP-LISTEN:1337,nodelay,reuseaddr,fork", "EXEC:'stdbuf -i0 -o0 -e0 python sim.py'"]
