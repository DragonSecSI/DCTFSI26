default := build
CHALL := $(notdir $(CURDIR))
DIST_DIR := dist

build: main.c gen_flag.py flag.txt
	python3 gen_flag.py
	gcc main_compile.c -O1 -ochall

dist: build
	mkdir -p $(DIST_DIR)
	cp chall $(DIST_DIR)/chall
	tar czvf "${CHALL}.tar.gz" --transform "s|^${DIST_DIR}|$(CHALL)|g" dist/*

clean:
	-rm -rf chall main_compile.c $(DIST_DIR) "${CHALL}.tar.gz"
