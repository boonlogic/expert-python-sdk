init:
	@virtualenv local-env; \
	. ./local-env/bin/activate; \
	pip install -r requirements.txt; \
	echo ""; \
	echo "virtual environment configured, use 'source local-env/bin/activate' to enable it"

test:
	coverage run -m nose tests/test_client.py
	coverage html

.PHONY: init test
