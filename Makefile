.PHONY: core-build core-run devcontainer-build app-build app-run app-up app-stop app-restart noir-chat


core-build:
	docker compose build noir-core

core-run:
	docker compose run noir-core


devcontainer-build: core-build
	docker compose -f .devcontainer/docker-compose.yml build noir-devcontainer


app-build: core-build
	docker compose build noir-app

app-run: app-build
	docker compose run --rm noir-app

app-up: app-build
	docker compose up -d noir-app

app-stop:
	docker stop noir-app

app-restart: app-stop app-up


noir-chat: app-build
	docker compose run --rm --entrypoint="python -m noir.scripts.chat" noir-app
