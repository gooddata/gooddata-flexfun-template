SHELL := /bin/bash

#######################################################################
# Setup of development environment
#######################################################################

.PHONY: init-secrets
init-secrets:
	# if needed, initialize files that are not committed to VCS
	touch .secrets && chmod 600 .secrets

.PHONY: dev
dev: init-secrets
	python3.11 -m venv .venv --upgrade-deps
	source .venv/bin/activate && pip3 install -r requirements.txt -r requirements-dev.txt
	.venv/bin/pre-commit install

.PHONY: mypy
mypy:
	.venv/bin/mypy --show-error-codes src

.PHONY: format-fix
format-fix:
	.venv/bin/ruff format .
	.venv/bin/ruff check . --fix --fixable I

.PHONY: fix-staged
fix-staged:
	pre-commit run --all-files


.PHONY: test
test:
	pytest tests

.PHONY: docker
docker:
	docker build -t flexfun-server:latest -f Dockerfile .

.PHONY: dev-server
dev-server:
	gooddata-flight-server \
	    start \
	    --config \
	        config/server.config.toml \
	        config/auth.config.toml \
	        config/flexfun.config.toml \
	    --dev-log
