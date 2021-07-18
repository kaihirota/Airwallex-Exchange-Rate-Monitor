.PHONY: test clean run

default: test

run:
	PYTHONPATH=$(pwd) python conversion_rate_analyzer/main.py data/10min_single_curr.jsonl

test:
	PYTHONPATH=$(pwd) pytest

clean: SHELL := /bin/bash
clean:
	rm .coverage
	rm -rf htmlcov
	rm -rf logs
	rm -rf .pytest_cache
	rm output/output.jsonl
	rm output/output_test.jsonl
