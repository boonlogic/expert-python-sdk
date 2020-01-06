init:
	pip install -r requirements.txt

test:
	coverage run -m nose tests/test_client.py
	coverage html

.PHONY: init test
