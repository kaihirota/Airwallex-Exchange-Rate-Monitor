import os
from unittest.mock import patch

import jsonlines

from conversion_rate_analyzer import config
from conversion_rate_analyzer.utils.writer import SpotRateWriter
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate

test_output_file = os.path.join(config.OUTPUT_DIR, "output_test.jsonl")


@patch('conversion_rate_analyzer.config.OUTPUT_FILE', test_output_file)
def test_writer(conversion_rate: CurrencyConversionRate):
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    SpotRateWriter().write(conversion_rate)
    assert os.path.exists(test_output_file)


@patch('conversion_rate_analyzer.config.OUTPUT_FILE', test_output_file)
@patch('conversion_rate_analyzer.config.VERBOSE', True)
def test_writer_verbose(conversion_rate: CurrencyConversionRate):
    if os.path.exists(test_output_file):
        os.remove(test_output_file)

    SpotRateWriter().write(conversion_rate, current_avg_rate=0.353529, pct_change=0.11)
    assert config.OUTPUT_FILE == test_output_file
    assert os.path.exists(test_output_file)
    reader = jsonlines.open(config.OUTPUT_FILE)
    data = reader.read()
    assert data.keys() == {"timestamp", "currencyPair", "alert", "rate", "average_rate", "pct_change"}
