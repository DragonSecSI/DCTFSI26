build:
	docker compose --project-directory ./challenge build

push: build
	docker compose --project-directory ./challenge push

run: build
	docker compose --project-directory ./challenge up

dist:
	zip -r dist.zip challenge/

install: dist
	ctf challenge install .

sync: dist
	ctf challenge sync .
