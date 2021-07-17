from datetime import datetime

import pytest
from pydantic.error_wrappers import ValidationError

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate


def test_currency_conversion_rate():
    obj = {"timestamp": 1554933784.023, "currencyPair": "CNYAUD", "rate": 0.39281}
    data = CurrencyConversionRate.parse_obj(obj)
    assert type(data) == CurrencyConversionRate
    assert data.get_datetime() == datetime.utcfromtimestamp(obj["timestamp"])


def test_currency_conversion_rate_missing_attributes():
    with pytest.raises(ValidationError):
        obj = {"timestamp": 1554933784.023, "currencyPair": "CNYAUD"}
        data = CurrencyConversionRate.parse_obj(obj)


def test_currency_conversion_rate_invalid_data():
    with pytest.raises(ValidationError) as excinfo:
        obj = {"timestamp": 999999999999999, "currencyPair": "CNYAUD", "rate": 0.39281}
        data = CurrencyConversionRate.parse_obj(obj)

    assert "timestamp must be Unix Timestamp" in str(excinfo.value)
