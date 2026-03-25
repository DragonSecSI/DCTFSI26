DOCKER_IMAGE=reg.seclab.si/vp/2026/intro-web:latest
DOCKER_OPTS=--platform=linux/amd64

build:
	docker build ${DOCKER_OPTS} -t ${DOCKER_IMAGE} .

push: build
	docker push ${DOCKER_IMAGE}

run: build
	docker run ${DOCKER_OPTS} -p 8000:8000 --rm --name intro-web ${DOCKER_IMAGE}

dist:
	zip dist.zip Dockerfile server.py

install: dist
	ctf challenge install .

sync: dist
	ctf challenge sync .
