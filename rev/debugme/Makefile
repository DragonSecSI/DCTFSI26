CC      := gcc
CFLAGS  := -O2 -Wall -Wextra
PYTHON  := python3
CHALL   := $(notdir $(CURDIR))
DIST_DIR := dist

.PHONY: all generate build dist clean

all: build

generate: solve.py
	${PYTHON} solve.py

build: generate main.c
	mkdir -p dist
	${CC} ${CFLAGS} main.c -o"dist/${CHALL}"

dist: build
	tar czvf "${CHALL}.tar.gz" --transform "s|^${DIST_DIR}|$(CHALL)|g" dist/*

clean:
	-rm -rf dist/ "${CHALL}.tar.gz" generated_data.h
