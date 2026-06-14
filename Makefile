.PHONY: core-build core-run devcontainer-build app-build app-run app-up app-stop app-restart test-multi-agent


core-build:
	docker compose build noire-core

core-run:
	docker compose run noire-core


devcontainer-build: core-build
	docker compose -f .devcontainer/docker-compose.yml build noire-devcontainer


app-build: core-build
	docker compose build noire-app

app-run: app-build
	docker compose run --rm noire-app

app-up: app-build
	docker compose up -d noire-app

app-stop:
	docker stop noire-app

app-restart: app-stop app-up


test-multi-agent: devcontainer-build
	docker compose -f .devcontainer/docker-compose.yml run --rm --entrypoint="env PYTHONPATH=/workspace/src python -m noire.scripts.chat" noire-devcontainer
