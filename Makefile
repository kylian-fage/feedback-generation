.PHONY: run-dev run-server run-client setup check-npm check-poetry install-api

run-dev:
	$(MAKE) -j2 run-server run-client

run-server:
	cd api/ && poetry run server

run-client:
	npm run client

check-npm:
	@command -v npm >/dev/null 2>&1 || { echo "npm is not installed, please visit 'https://nodejs.org/en/download/'"; exit 1; }

check-poetry:
	@command -v poetry >/dev/null 2>&1 || { echo "poetry is not installed, please visit 'https://python-poetry.org/docs/#installation'"; exit 1; }

install-api: check-poetry
	cd api/ && poetry install

setup: check-npm check-poetry
	npm install && $(MAKE) install-api
