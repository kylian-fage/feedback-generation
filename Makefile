.PHONY: run-dev run-server run-client setup check-npm install-python-requirements setup-venv upgrade-pip

VENV = .venv/bin

run-dev:
	$(MAKE) -j2 run-server run-client

run-server:
	$(VENV)/python api/api/api.py

run-client:
	npm run client

check-npm:
	npm -v || (echo "npm is not installed, please visit 'https://nodejs.org/en/download/'" && exit 1)

setup-venv:
	python -m venv .venv

upgrade-pip:
	$(VENV)/python -m pip install --upgrade pip

install-python-requirements: setup-venv upgrade-pip
	$(VENV)/pip install -r api/requirements.txt

setup: check-npm
	npm install && $(MAKE) install-python-requirements
