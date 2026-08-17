DOCKER_IMAGE=registry.vuln.si/dctf26/web/pantry
DOCKER_OPTS=--platform=linux/amd64

build:
	docker build ${DOCKER_OPTS} -t ${DOCKER_IMAGE} .

push: build
	docker push ${DOCKER_IMAGE}

run: build
	docker run ${DOCKER_OPTS} -p 8000:8000 --rm --name web-pantry ${DOCKER_IMAGE}

dist:
	zip -r pantry.zip chall Dockerfile

install: dist
	ctf challenge install .

sync: dist
	ctf challenge sync .
