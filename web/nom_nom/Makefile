DOCKER_IMAGE=registry.dctf.si/web/nom-nom
DOCKER_OPTS=--platform=linux/amd64

build:
	docker build ${DOCKER_OPTS} -t ${DOCKER_IMAGE} .

push: build
	docker push ${DOCKER_IMAGE}

run: build
	docker run ${DOCKER_OPTS} -p 8000:8000 --rm --name web-nom-nom ${DOCKER_IMAGE}

dist:
	zip -r nom_nom.zip chall Dockerfile

install: dist
	ctf challenge install .

sync: dist
	ctf challenge sync .
