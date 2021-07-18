import logging
import os
from pathlib import Path
from typing import Dict

from _pytest.logging import caplog as _caplog
import pytest
from loguru import logger

from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate

PROJECT_ROOT_DIR = Path(__file__).parent.parent


@pytest.fixture
def caplog(_caplog):
    """for testing logging message content"""

    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)


@pytest.fixture
def path_input_file_sample() -> str:
    return os.path.join(PROJECT_ROOT_DIR, "input/input1.jsonl")


@pytest.fixture
def path_input_file_10min_single_curr_stream() -> str:
    return os.path.join(PROJECT_ROOT_DIR, "input/10min_single_curr.jsonl")


@pytest.fixture
def path_input_file_10min_single_curr_stream_outoforder() -> str:
    return os.path.join(PROJECT_ROOT_DIR, "input/10min_single_curr_out_of_order.jsonl")


@pytest.fixture
def path_input_file_nonexistent() -> str:
    return os.path.join(PROJECT_ROOT_DIR, "input/input_test.jsonl")


@pytest.fixture
def path_output_file_test() -> str:
    fpath = os.path.join(PROJECT_ROOT_DIR, "output/output_test.jsonl")
    if os.path.exists(fpath):
        os.remove(fpath)
    return fpath


@pytest.fixture
def conversion_data_valid() -> Dict:
    return {"timestamp": 1554933784.023, "currencyPair": "CNYAUD", "rate": 0.39281}


@pytest.fixture
def conversion_data_missing() -> Dict:
    return {"timestamp": 1554933784.023, "currencyPair": "CNYAUD"}


@pytest.fixture
def conversion_data_invalid() -> Dict:
    return {"timestamp": 999999999999999, "currencyPair": "CNYAUD", "rate": 0.39281}


@pytest.fixture
def conversion_rate_valid(conversion_data_valid: Dict) -> CurrencyConversionRate:
    return CurrencyConversionRate.parse_obj(conversion_data_valid)


@pytest.fixture
def conversion_rate_missing(conversion_data_missing) -> CurrencyConversionRate:
    return CurrencyConversionRate.parse_obj(conversion_data_missing)


@pytest.fixture
def conversion_rate_invalid(conversion_data_invalid) -> CurrencyConversionRate:
    return CurrencyConversionRate.parse_obj(conversion_data_invalid)
