import os
import sys
from typing import Dict
from unittest.mock import patch

import jsonlines
from jsonlines import InvalidLineError
import pytest

from conversion_rate_analyzer import config
from conversion_rate_analyzer.main import main


@patch("sys.argv", ["conversion_rate_analyzer/main.py"])
def test_main_omit_input_file():
    with pytest.raises(IndexError):
        main()


@patch("sys.argv", ["conversion_rate_analyzer/main.py", "foo.jsonl"])
def test_main_nonexistent_input_file():
    with pytest.raises(FileNotFoundError):
        main()


def test_main_invalid_input_file(caplog, path_input_file_nonexistent: str, conversion_data_missing: Dict):
    test_input_file = path_input_file_nonexistent

    if os.path.exists(test_input_file):
        os.remove(test_input_file)

    writer = jsonlines.open(test_input_file, "a")
    writer.write(conversion_data_missing)
    writer.close()

    with patch.object(sys, "argv", ["conversion_rate_analyzer/main.py", test_input_file]):
        main()

    assert "field required (type=value_error.missing)" in caplog.text
    os.remove(test_input_file)


@patch("sys.argv", ["conversion_rate_analyzer/main.py", "input/input1.jsonl"])
def test_main(path_output_file_test: str):
    main()
    reader = jsonlines.open(config.OUTPUT_FILE)

    assert reader.read() == {"timestamp": 1554933794.023, "currencyPair": "CNYAUD", "alert": "spotChange"}
    from conversion_rate_analyzer.main import data_points_processed
    assert data_points_processed == 11


@patch("sys.argv", ["conversion_rate_analyzer/main.py", "input/testinput1.jsonl"])
def test_main_invalid_jsonline(path_input_file_sample: str, path_output_file_test: str):
    reader = jsonlines.open(path_input_file_sample)

    path, filename = os.path.split(path_input_file_sample)
    new_file = os.path.join(path, "test" + filename)
    writer = jsonlines.open(new_file, "w")

    for obj in reader:
        writer.write(obj)

    writer.close()

    with open(new_file, "a") as f:
        f.write("invalid line")

    with pytest.raises(InvalidLineError):
        main()

    os.remove(new_file)
