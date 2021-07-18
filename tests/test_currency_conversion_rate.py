from datetime import datetime
from typing import Dict

import pytest
from pydantic.error_wrappers import ValidationError

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate


def test_currency_conversion_rate(conversion_data_valid: Dict):
    data = CurrencyConversionRate.parse_obj(conversion_data_valid)
    assert type(data) == CurrencyConversionRate
    assert data.get_datetime() == datetime.utcfromtimestamp(conversion_data_valid["timestamp"])


def test_currency_conversion_rate_missing_attributes(conversion_data_missing: Dict):
    with pytest.raises(ValidationError):
        data = CurrencyConversionRate.parse_obj(conversion_data_missing)


def test_currency_conversion_rate_invalid_data(conversion_data_invalid: Dict):
    with pytest.raises(ValidationError) as excinfo:
        data = CurrencyConversionRate.parse_obj(conversion_data_invalid)

    assert "timestamp must be Unix Timestamp" in str(excinfo.value)
