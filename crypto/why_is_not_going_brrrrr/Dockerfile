FROM python:3.12-slim
WORKDIR /app

RUN apt-get -y update && \
    apt-get install -y socat coreutils && \
    rm -rf /var/lib/apt/lists/*

COPY gobrrrrr.py /app

RUN chmod 555 gobrrrrr.py

CMD ["socat", "-T", "10", "TCP-LISTEN:1337,nodelay,reuseaddr,fork", "EXEC:'stdbuf -i0 -o0 -e0 python gobrrrrr.py'"]
