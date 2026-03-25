CC     = zig cc
CFLAGS = -O1 -std=c11
SRC    = game.c

all:
	$(CC) $(CFLAGS) -target x86_64-linux-gnu       -o game-linux-x86_64     $(SRC)
	$(CC) $(CFLAGS) -target aarch64-linux-gnu      -o game-linux-aarch64    $(SRC)
	$(CC) $(CFLAGS) -target arm-linux-gnueabihf    -o game-linux-arm        $(SRC)
	$(CC) $(CFLAGS) -target x86_64-macos           -o game-macos-x86_64     $(SRC)
	$(CC) $(CFLAGS) -target aarch64-macos          -o game-macos-aarch64    $(SRC)
	$(CC) $(CFLAGS) -target x86_64-freebsd         -o game-freebsd-x86_64   $(SRC)
	$(CC) $(CFLAGS) -target aarch64-freebsd        -o game-freebsd-aarch64  $(SRC)

clean:
	rm -f game-linux-* game-macos-* game-freebsd-*

.PHONY: all clean
