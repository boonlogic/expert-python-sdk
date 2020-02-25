
init:
	@virtualenv local-env; \
	. ./local-env/bin/activate; \
	pip install -r requirements.txt; \
	echo ""; \
	echo "virtual environment configured, use 'source local-env/bin/activate' to enable it"

test: local-env-check
	@source local-env/bin/activate; \
	cd tests ; \
	coverage run --source=boonnano -m nose -verbosity=2 test_client.py; \
	coverage html

pypi:
	@source local-env/bin/activate; \
	python setup.py sdist; \
	twine upload --skip-existing dist/*

local-env-check:
	@if [ ! -d ./local-env ]; then \
		echo "must run 'make init' first"; \
		exit 1; \
	fi

.PHONY: init test pypi local-env-check
