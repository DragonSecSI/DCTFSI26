FROM alpine:3.21
WORKDIR /app

RUN apk add --no-cache socat coreutils

COPY app .
COPY flag.txt .

CMD ["socat", "-T", "30", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'stdbuf -i0 -o0 -e0 ./app'"]
