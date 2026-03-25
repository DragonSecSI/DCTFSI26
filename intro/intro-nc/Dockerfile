FROM alpine:3.23
WORKDIR /app

RUN apk add --no-cache socat python3

COPY server.py /app
CMD ["socat", "-T", "10", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 server.py'"]
