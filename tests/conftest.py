import logging
import os
from pathlib import Path

from loguru import logger
import pytest
from _pytest.logging import caplog as _caplog

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate

PROJECT_ROOT_DIR = Path(__file__).parent.parent


@pytest.fixture
def sample_input_path() -> str:
    return os.path.join(PROJECT_ROOT_DIR, "example/input1.jsonl")


@pytest.fixture
def conversion_rate() -> CurrencyConversionRate:
    obj = {"timestamp": 1554933784.023, "currencyPair": "CNYAUD", "rate": 0.39281}
    return CurrencyConversionRate.parse_obj(obj)


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)
