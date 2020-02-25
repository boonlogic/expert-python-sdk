init:
	which python3
	python3 -m venv local-env


#; \
#	. local-env/bin/activate; \
#	pip3 install -r requirements.txt; \
#	echo ""; \
#	echo "virtual environment configured, use 'source local-env/bin/activate' to enable it"

test: local-env-check
	@. local-env/bin/activate; \
	cd tests ; \
	coverage run --source=boonnano -m nose -verbosity=2 test_client.py; \
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

.PHONY: init test pypi local-env-check
