.PHONY: core-build core-run devcontainer-build app-build app-run app-up app-stop app-restart mongo-start mongo-stop mongo-restart qdrant-start qdrant-stop qdrant-restart noir-chat pixoo-space-invaders


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


mongo-start:
	docker compose up -d noir-mongo

mongo-stop:
	docker compose stop noir-mongo

mongo-restart: mongo-stop mongo-start


qdrant-start:
	docker compose up -d noir-qdrant

qdrant-stop:
	docker compose stop noir-qdrant

qdrant-restart: qdrant-stop qdrant-start


pixoo-display: app-build
	docker compose run --rm --entrypoint="python -m noir.scripts.pixoo.pixoo_display" noir-app

noir-chat: app-build
	docker compose run --rm --entrypoint="python -m noir.scripts.noir.chat" noir-app
