import os
import sys
from unittest.mock import patch

import jsonlines
import pytest


from conversion_rate_analyzer import config
from conversion_rate_analyzer.main import main

test_output_file = os.path.join(config.OUTPUT_DIR, "output_test.jsonl")


@patch("sys.argv", ["conversion_rate_analyzer/main.py"])
def test_main_omit_input_file():
    with pytest.raises(IndexError):
        main()


@patch("sys.argv", ["conversion_rate_analyzer/main.py", "foo.jsonl"])
def test_main_nonexistent_input_file():
    with pytest.raises(FileNotFoundError):
        main()


def test_main_invalid_input_file(caplog):
    test_input_file = os.path.join(config.PROJECT_ROOT_DIR, "data/input_test.jsonl")

    if os.path.exists(test_input_file):
        os.remove(test_input_file)

    writer = jsonlines.open(test_input_file, "a")
    writer.write({"timestamp": 1554933784.023, "currencyPair": "CNYAUD"})
    writer.close()

    with patch.object(sys, "argv", ["conversion_rate_analyzer/main.py", test_input_file]):
        main()
        assert "field required (type=value_error.missing)" in caplog.text

    os.remove(test_input_file)


@patch("sys.argv", ["conversion_rate_analyzer/main.py", "example/input1.jsonl"])
def test_main():
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    main()
    reader = jsonlines.open(config.OUTPUT_FILE)
    assert reader.read() == {"timestamp": 1554933794.023, "currencyPair": "CNYAUD", "alert": "spotChange"}
    from conversion_rate_analyzer.main import data_points_processed
    assert data_points_processed == 11
