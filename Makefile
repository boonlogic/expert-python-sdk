export SHELL := /bin/bash

init:
	python3 -m venv local-env && \
	. local-env/bin/activate && \
	pip3 install --upgrade pip && \
	pip3 install -r requirements.txt && \
	echo "" && \
	echo "virtual environment configured, use 'source local-env/bin/activate' to enable it"

format-check: format
	git diff --exit-code; if [ $$? -ne 0 ]; then echo "format-check failed"; exit 1; fi; \
	echo "*** format-check passed"

format:
	@. local-env/bin/activate && \
	pip install black && \
	black boonnano

test: local-env-check
	@. local-env/bin/activate && \
	cd tests && \
	coverage run --source=boonnano -m pytest -x -vv test_client.py && \
	coverage html

pypi:
	@. local-env/bin/activate; \
	python3 setup.py sdist; \
	twine upload --skip-existing dist/*

local-env-check:
	@if [ ! -d ./local-env ]; then \
		echo "must run 'make init' first"; \
		exit 1; \
	fi

docs:
	@. local-env/bin/activate; \
	pdoc3 --force -o docs --html boonnano

.PHONY: docs init test pypi local-env-check
