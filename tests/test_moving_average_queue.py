import os
from unittest.mock import patch

import jsonlines
import pytest

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.service.moving_average_monitor import MovingAverageMonitor
from conversion_rate_analyzer.utils.exceptions import SpotRateWriterError
from conversion_rate_analyzer.utils.reader import SpotRateReader


def test_singleton():
    monitor1 = MovingAverageMonitor()
    monitor2 = MovingAverageMonitor()
    assert monitor1 == monitor2


def test_moving_average_10min_single_curr(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        monitor.process_new_rate(data)

    monitor.terminate_writer()

    currency_pair = "AUDUSD"
    assert monitor.currency_pair_exists(currency_pair) is True
    assert monitor.get_known_currency_pairs() == {currency_pair}
    assert monitor.get_current_queue_size(currency_pair=currency_pair) == 300
    assert round(monitor.get_current_average_rate(currency_pair=currency_pair), 9) == round(0.9971610538071796, 9)


def test_moving_average_10min_single_curr_out_of_order(
        path_input_file_10min_single_curr_stream_outoforder: str,
        path_output_file_test: str
):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream_outoforder)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        monitor.process_new_rate(data)

    monitor.terminate_writer()

    currency_pair = "AUDUSD"
    items = []
    while not monitor.conversion_rates_queue[currency_pair].empty():
        ts, rate = monitor.conversion_rates_queue[currency_pair].get()
        items += ts,

    start = 1626609915
    assert items == list(range(start, start + 300))


def test_moving_average_get_queue_size_unknown_currency_pair(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        monitor.process_new_rate(data)

    monitor.terminate_writer()

    currency_pair = "AUDJPY"
    with pytest.raises(KeyError) as excinfo:
        monitor.get_current_queue_size(currency_pair)

    assert f"The currency pair ({currency_pair}) does not exist" in str(excinfo.value)


def test_moving_average_get_average_rate_unknown_currency_pair(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        monitor.process_new_rate(data)

    monitor.terminate_writer()

    currency_pair = "AUDJPY"
    with pytest.raises(KeyError) as excinfo:
        monitor.get_current_average_rate(currency_pair)

    assert f"The currency pair ({currency_pair}) does not exist" in str(excinfo.value)


@patch("conversion_rate_analyzer.config.VERBOSE", True)
def test_moving_average_verbose(path_input_file_10min_single_curr_stream: str, path_output_file_test: str):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        monitor.process_new_rate(data)

    monitor.terminate_writer()

    reader = jsonlines.open(path_output_file_test)
    data = reader.read()
    assert data.keys() == {"timestamp", "currencyPair", "alert", "rate", "average_rate", "pct_change"}


def test_moving_average_uninitialized_writer(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    monitor = MovingAverageMonitor()
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

    with pytest.raises(SpotRateWriterError):
        for obj in reader:
            data = CurrencyConversionRate.parse_obj(obj)
            monitor.process_new_rate(data)


def test_moving_average_delete_output_file(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str
):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    reader = SpotRateReader().jsonlines_reader(path_input_file_10min_single_curr_stream)

    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        monitor.process_new_rate(data)

    os.remove(path_output_file_test)

    with pytest.raises(SpotRateWriterError) as excinfo:
        monitor.terminate_writer()

    assert "Output file has been removed before closing." in str(excinfo.value)


def test_moving_average_initialize_twice(
        path_input_file_10min_single_curr_stream: str,
        path_output_file_test: str,
):
    monitor = MovingAverageMonitor()
    monitor.initialize_writer(path_output_file_test)
    path, file = os.path.split(path_output_file_test)
    new_path = os.path.join(path, 'test' + file)
    monitor.initialize_writer(new_path)
    assert monitor.jsonline_writer.path == new_path
    assert os.path.exists(new_path)
    os.remove(new_path)
