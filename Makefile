.PHONY: tests
tests: 
	pytest --cov=pr_status_action tests.py --cov-report term --cov-fail-under=100
