.PHONY: test clean

default: test

test:
	PYTHONPATH=$(pwd) pytest

clean:
	rm .coverage
	rm -rf htmlcov
	rm -rf logs
	rm -rf output
	rm -rf .pytest_cache