init:
	pip install -r requirements.txt

test:
	coverage run -m nose test_client.py
	coverage html

.PHONY: init test
