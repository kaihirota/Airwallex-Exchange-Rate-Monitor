import os

import jsonlines
from jsonlines.jsonlines import Writer
from loguru import logger

from conversion_rate_analyzer import config
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate


@logger.catch
class SpotRateWriter:
    """Class for writing conversion rates that exceed acceptance threshold percentage."""

    @staticmethod
    def write(data: CurrencyConversionRate, current_avg_rate: float = None, pct_change: float = None):
        """
        Appends the data to the output file specified in the config file.
        If the file does not exist, new file will be created.
        """
        out = data.dict()

        if config.VERBOSE:
            out["average_rate"] = current_avg_rate
            out["pct_change"] = pct_change
        else:
            del out["rate"]

        out["alert"] = "spotChange"

        if not os.path.exists(config.OUTPUT_FILE):
            logger.info(f"Output file ({config.OUTPUT_FILE}) does not exist. Creating file.")

        writer: Writer = jsonlines.open(config.OUTPUT_FILE, mode='a')
        writer.write(out)
        writer.close()
