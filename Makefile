.PHONY: test clean run

default: test

run:
	PYTHONPATH=$(pwd) python conversion_rate_analyzer/main.py data/10min.jsonl

test:
	PYTHONPATH=$(pwd) pytest

clean:
	rm .coverage
	rm -rf htmlcov
	rm -rf logs
	rm -rf output
	rm -rf .pytest_cache