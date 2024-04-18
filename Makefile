.PHONY: run-dev run-server run-client setup check-npm check-poetry install-api

VENV = .venv/bin

run-dev:
	$(MAKE) -j2 run-server run-client

run-server:
	cd api/ && poetry run server

run-client:
	npm run client

check-npm:
	npm -v || (echo "npm is not installed, please visit 'https://nodejs.org/en/download/'" && exit 1)

check-poetry:
	poetry -V || (echo "poetry is not installed, please visit 'https://python-poetry.org/docs/#installation'" && exit 1)

install-api: check-poetry
	cd api/ && poetry install

setup: check-npm check-poetry
	npm install && $(MAKE) install-api
