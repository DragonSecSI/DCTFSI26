#!/bin/bash

docker build -t glibc-builder -f Dockerfile.build .
docker run --rm -v $(pwd):/build -u $(id -u):$(id -g) glibc-builder bash -c "\
	clang++ -o main main.cpp \
	  -Wl,--rpath=. \
		-Wl,--dynamic-linker=./ld-linux-x86-64.so.2
"

cid=$(docker create --name temp glibc-builder)
docker cp $cid:/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 ./ld-linux-x86-64.so.2
docker cp $cid:/usr/lib/x86_64-linux-gnu/libc.so.6 ./libc.so.6
docker rm -f $cid

env LD_TRACE_LOADED_OBJECTS=1 ./main
