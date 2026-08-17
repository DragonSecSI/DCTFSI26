DOCKER_IMAGE=registry.vuln.si/dctf26/pwn/trivia
DOCKER_OPTS=--platform=linux/amd64

build:
	docker build ${DOCKER_OPTS} -t ${DOCKER_IMAGE} .

push: build
	docker push ${DOCKER_IMAGE}

run: build
	docker run ${DOCKER_OPTS} -p 1337:1337 --rm --name pwn-trivia ${DOCKER_IMAGE}

dist:
	mv src/app src/tmpapp
	mv src/player_app src/app
	zip dist.zip Dockerfile src/app src/*.txt
	mv src/app src/player_app
	mv src/tmpapp src/app

install: dist
	ctf challenge install .

sync: dist
	ctf challenge sync .
