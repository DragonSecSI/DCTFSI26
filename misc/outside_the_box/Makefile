DOCKER_IMAGE=registry.dctf.si/misc/outside-the-box
DOCKER_OPTS=--platform=linux/amd64

build:
	docker build ${DOCKER_OPTS} -t ${DOCKER_IMAGE} .

push: build
	docker push ${DOCKER_IMAGE}

run: build
	docker run ${DOCKER_OPTS} -p 1337:1337 --rm --name outside_the_box ${DOCKER_IMAGE}

dist:
	zip dist.zip Dockerfile server.py

install: dist
	ctf challenge install .

sync: dist
	ctf challenge sync .
