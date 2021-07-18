import os
from unittest.mock import patch

import jsonlines

from conversion_rate_analyzer import config
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.utils.writer import SpotRateWriter


def test_writer(conversion_rate_valid: CurrencyConversionRate, path_output_file_test: str):
    with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
        SpotRateWriter().write(conversion_rate_valid)

    assert os.path.exists(path_output_file_test)


@patch("conversion_rate_analyzer.config.VERBOSE", True)
def test_writer_verbose(conversion_rate_valid: CurrencyConversionRate, path_output_file_test: str):
    with patch("conversion_rate_analyzer.config.OUTPUT_FILE", path_output_file_test):
        SpotRateWriter().write(conversion_rate_valid, current_avg_rate=0.353529, pct_change=0.11)
        reader = jsonlines.open(config.OUTPUT_FILE)
        data = reader.read()

    assert data.keys() == {"timestamp", "currencyPair", "alert", "rate", "average_rate", "pct_change"}
