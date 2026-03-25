FROM debian:latest
WORKDIR /app

RUN apt-get update && apt-get install -y socat coreutils verilator

COPY app .
COPY server.hex .

CMD ["socat", "-T", "30", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'stdbuf -i0 -o0 -e0 ./app'"]
