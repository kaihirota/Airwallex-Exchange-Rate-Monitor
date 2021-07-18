from jsonlines.jsonlines import Reader
import pytest
from typing import Dict

from conversion_rate_analyzer.utils.reader import SpotRateReader


def test_jsonlines_reader_invalid_input_file():
    with pytest.raises(FileNotFoundError):
        SpotRateReader().jsonlines_reader("foo.jsonl")


def test_jsonlines_reader(path_input_file_sample: str, conversion_data_valid: Dict):
    reader = SpotRateReader().jsonlines_reader(path_input_file_sample)
    assert type(reader) == Reader
    assert reader.read() == conversion_data_valid
