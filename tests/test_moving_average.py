import os
from unittest.mock import patch

import jsonlines
import pytest

from conversion_rate_analyzer import config
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.moving_average import MovingAverageQueue
from conversion_rate_analyzer.utils.reader import SpotRateReader
from conversion_rate_analyzer.utils.writer import SpotRateWriter

test_input_file = os.path.join(config.PROJECT_ROOT_DIR, "example/input1.jsonl")
test_input_file_10min = os.path.join(config.PROJECT_ROOT_DIR, "data/10min.jsonl")
test_output_file = os.path.join(config.OUTPUT_DIR, "output_test.jsonl")


def test_singleton():
    queue1 = MovingAverageQueue()
    queue2 = MovingAverageQueue()
    assert queue1 == queue2


@patch("sys.argv", ["conversion_rate_analyzer/main.py", test_input_file_10min])
@patch("conversion_rate_analyzer.config.OUTPUT_FILE", test_output_file)
def test_moving_average_10min():
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    queue = MovingAverageQueue()
    reader = SpotRateReader().jsonlines_reader(test_input_file_10min)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        queue.process_new_rate(data)

    currency_pair = "AUDUSD"
    assert queue.currency_pair_exists(currency_pair) is True
    assert queue.get_known_currency_pairs() == {currency_pair}
    assert queue.get_current_queue_size(currency_pair=currency_pair) == 300
    assert round(queue.get_current_average_rate(currency_pair=currency_pair), 9) == round(1.0081539678695328, 9)


@patch("sys.argv", ["conversion_rate_analyzer/main.py", test_input_file_10min])
@patch("conversion_rate_analyzer.config.OUTPUT_FILE", test_output_file)
def test_moving_average_get_queue_size_unknown_currency_pair():
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    queue = MovingAverageQueue()
    reader = SpotRateReader().jsonlines_reader(test_input_file_10min)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        queue.process_new_rate(data)

    currency_pair = "AUDJPY"
    with pytest.raises(KeyError) as excinfo:
        queue.get_current_queue_size(currency_pair)

    assert f"The currency pair ({currency_pair}) does not exist" in str(excinfo.value)


@patch("sys.argv", ["conversion_rate_analyzer/main.py", test_input_file_10min])
@patch("conversion_rate_analyzer.config.OUTPUT_FILE", test_output_file)
def test_moving_average_get_average_rate_unknown_currency_pair():
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    queue = MovingAverageQueue()
    reader = SpotRateReader().jsonlines_reader(test_input_file_10min)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        queue.process_new_rate(data)

    currency_pair = "AUDJPY"
    with pytest.raises(KeyError) as excinfo:
        queue.get_current_average_rate(currency_pair)

    assert f"The currency pair ({currency_pair}) does not exist" in str(excinfo.value)


@patch("sys.argv", ["conversion_rate_analyzer/main.py", test_input_file_10min])
@patch("conversion_rate_analyzer.config.OUTPUT_FILE", test_output_file)
@patch("conversion_rate_analyzer.config.VERBOSE", True)
def test_moving_average_verbose():
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    queue = MovingAverageQueue()
    reader = SpotRateReader().jsonlines_reader(test_input_file_10min)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        queue.process_new_rate(data)

    assert config.OUTPUT_FILE == test_output_file
    assert os.path.exists(test_output_file)
    reader = jsonlines.open(test_output_file)
    data = reader.read()
    assert data.keys() == {"timestamp", "currencyPair", "alert", "rate", "average_rate", "pct_change"}
