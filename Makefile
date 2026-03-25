SHELL:=/bin/bash
FOLDERS="intro"
REGISTRY=ghcr.io/dragonsecsi/dctfsi26
TAG=latest
BUILD_IMAGE=builder:latest

build:
	for folder in ${FOLDERS}; do \
	  pushd $$folder; \
		for chall in $$(ls -d */); do \
		  pushd $$chall; \
			make build; \
		  popd; \
		done; \
		popd; \
	done

push:
	for folder in ${FOLDERS}; do \
	  pushd $$folder; \
		for chall in $$(ls -d */); do \
		  pushd $$chall; \
			make push; \
		  popd; \
		done; \
		popd; \
	done

dist:
	for folder in ${FOLDERS}; do \
	  pushd $$folder; \
		for chall in $$(ls -d */); do \
		  pushd $$chall; \
			make dist; \
		  popd; \
		done; \
		popd; \
	done

install:
	for folder in ${FOLDERS}; do \
	  pushd $$folder; \
		for chall in $$(ls -d */); do \
		  pushd $$chall; \
			make install; \
		  popd; \
		done; \
		popd; \
	done

sync:
	for folder in ${FOLDERS}; do \
	  pushd $$folder; \
		for chall in $$(ls -d */); do \
		  pushd $$chall; \
			make sync; \
		  popd; \
		done; \
		popd; \
	done

builder:
	docker build -t ${BUILD_IMAGE} --platform=linux/amd64 ./builder
