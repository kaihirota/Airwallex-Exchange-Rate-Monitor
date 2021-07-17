from jsonlines.jsonlines import Reader
import pytest

from conversion_rate_analyzer.utils.reader import SpotRateReader


def test_jsonlines_reader_invalid_input_file():
    with pytest.raises(FileNotFoundError):
        SpotRateReader().jsonlines_reader("foo.jsonl")


def test_jsonlines_reader(sample_input_path: str):
    reader = SpotRateReader().jsonlines_reader(sample_input_path)
    assert type(reader) == Reader
    assert reader.read() == {"timestamp": 1554933784.023, "currencyPair": "CNYAUD", "rate": 0.39281}
