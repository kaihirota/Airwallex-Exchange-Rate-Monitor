import os
from unittest.mock import patch

import jsonlines

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.utils.writer import SpotRateWriter


def test_writer(conversion_rate_valid: CurrencyConversionRate, path_output_file_test: str):
    writer = SpotRateWriter(path_output_file_test)
    writer.write(conversion_rate_valid)
    writer.close()
    assert os.path.exists(path_output_file_test)


@patch("conversion_rate_analyzer.config.VERBOSE", True)
def test_writer_verbose(conversion_rate_valid: CurrencyConversionRate, path_output_file_test: str):
    writer = SpotRateWriter(path_output_file_test)
    writer.write(conversion_rate_valid, current_avg_rate=0.353529, pct_change=0.11)
    writer.close()

    reader = jsonlines.open(path_output_file_test)
    data = reader.read()
    assert data.keys() == {"timestamp", "currencyPair", "alert", "rate", "average_rate", "pct_change"}
