CC      := gcc
CFLAGS  := -O2 -Wall -Wextra
PYTHON  := python3
CHALL   := $(notdir $(CURDIR))
DIST_DIR := dist

.PHONY: all generate build solve dist clean

all: build

generate: solve.py
	$(PYTHON) solve.py --emit-header --output sat_data.h

build: generate main.c
	mkdir -p dist
	${CC} ${CFLAGS} main.c -o"dist/${CHALL}"

solve: generate
	$(PYTHON) solve.py --solve

dist: build
	tar czvf "${CHALL}.tar.gz" --transform "s|^${DIST_DIR}|$(CHALL)|g" dist/*

clean:
	-rm -rf dist/ "${CHALL}.tar.gz" sat_data.h
