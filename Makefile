.PHONY: test clean run

default: all

run:
	PYTHONPATH=$(pwd) python conversion_rate_analyzer/main.py input/10min_single_curr.jsonl

test:
	PYTHONPATH=$(pwd) pytest

clean: SHELL := /bin/bash
clean:
	rm .coverage
	rm -rf htmlcov
	rm -rf logs
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm output/output_test.jsonl
	rm output/2021*.jsonl

all: test clean
