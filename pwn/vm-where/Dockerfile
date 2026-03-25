FROM ubuntu:26.04
WORKDIR /app

RUN apt-get update && apt-get -y install socat

COPY main main
COPY ld-linux-x86-64.so.2 ld-linux-x86-64.so.2
COPY libc.so.6 libc.so.6
CMD ["socat", "-T", "10", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'./main'"]
