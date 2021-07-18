from unittest.mock import patch

import jsonlines
import pytest

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.moving_average import MovingAverageQueue
from conversion_rate_analyzer.utils.reader import SpotRateReader


def test_singleton():
    queue1 = MovingAverageQueue()
    queue2 = MovingAverageQueue()
    assert queue1 == queue2


def test_moving_average_10min_single_curr(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    with patch("sys.argv", ["conversion_rate_analyzer/main.py", path_input_file_10min_single_curr_stream]):
        with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
            queue = MovingAverageQueue()
            reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

            for obj in reader:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)

    currency_pair = "AUDUSD"
    assert queue.currency_pair_exists(currency_pair) is True
    assert queue.get_known_currency_pairs() == {currency_pair}
    assert queue.get_current_queue_size(currency_pair=currency_pair) == 300
    assert round(queue.get_current_average_rate(currency_pair=currency_pair), 9) == round(0.9934236150574627, 9)


def test_moving_average_10min_single_curr_out_of_order(
        path_input_file_10min_single_curr_stream_outoforder: str,
        path_output_file_test: str
):
    with patch("sys.argv", ["conversion_rate_analyzer/main.py", path_input_file_10min_single_curr_stream_outoforder]):
        with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
            queue = MovingAverageQueue()
            reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream_outoforder)

            for obj in reader:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)

    currency_pair = "AUDUSD"
    items = []
    while not queue.conversion_rates_queue[currency_pair].empty():
        ts, rate = queue.conversion_rates_queue[currency_pair].get()
        items += ts,

    start = 1626594160
    assert items == list(range(start, start + 300))


def test_moving_average_get_queue_size_unknown_currency_pair(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    with patch("sys.argv", ["conversion_rate_analyzer/main.py", path_input_file_10min_single_curr_stream]):
        with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
            queue = MovingAverageQueue()
            reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

            for obj in reader:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)

    currency_pair = "AUDJPY"
    with pytest.raises(KeyError) as excinfo:
        queue.get_current_queue_size(currency_pair)

    assert f"The currency pair ({currency_pair}) does not exist" in str(excinfo.value)


def test_moving_average_get_average_rate_unknown_currency_pair(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    with patch("sys.argv", ["conversion_rate_analyzer/main.py", path_input_file_10min_single_curr_stream]):
        with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
            queue = MovingAverageQueue()
            reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

            for obj in reader:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)

    currency_pair = "AUDJPY"
    with pytest.raises(KeyError) as excinfo:
        queue.get_current_average_rate(currency_pair)

    assert f"The currency pair ({currency_pair}) does not exist" in str(excinfo.value)


@patch("conversion_rate_analyzer.config.VERBOSE", True)
def test_moving_average_verbose(path_input_file_10min_single_curr_stream: str, path_output_file_test: str):
    with patch("sys.argv", ["conversion_rate_analyzer/main.py", path_input_file_10min_single_curr_stream]):
        with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
            queue = MovingAverageQueue()
            reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

            for obj in reader:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)

    reader = jsonlines.open(path_output_file_test)
    data = reader.read()
    assert data.keys() == {"timestamp", "currencyPair", "alert", "rate", "average_rate", "pct_change"}
