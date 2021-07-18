import sys
import time
from pathlib import Path

from jsonlines import InvalidLineError
from loguru import logger
from pydantic.error_wrappers import ValidationError

PROJECT_ROOT_DIR = str(Path(__file__).parent.parent)
if PROJECT_ROOT_DIR not in sys.path:  # pragma: no cover
    sys.path.append(PROJECT_ROOT_DIR)

from conversion_rate_analyzer import config
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.service.moving_average_monitor import MovingAverageMonitor
from conversion_rate_analyzer.utils.exceptions import SpotRateWriterError
from conversion_rate_analyzer.utils.reader import SpotRateReader

data_points_processed = 0

"""
The program:
- reads from input jsonline file passed via command line argument,
- convert each line into a CurrencyConversionRate object after validating data,
- and uses the MovingAverageMonitor singleton object to record conversion rates for each currency pair
  while retaining a specific number of latest n records for continuously updating moving averages
- when the percentage difference between a new conversion rate and the current moving average exceed
  the acceptance threshold, the program will print to the console and log that alert to the output file
- all logs are captured and stored in `logs` directory as well
"""


def main():
    if len(sys.argv) < 2:
        e = IndexError("Supply the input file path as an argument: python main.py input.jsonl")
        logger.error(e)
        raise e

    input_file = sys.argv[1]
    logger.info(
        (
            "Program starting with parameters:"
            f"\n\tInput File: {input_file}"
            f"\n\tOutput File: {config.OUTPUT_FILE}"
            f"\n\tMoving Average Window Size: {config.MOVING_AVERAGE_WINDOW} ({config.MOVING_AVERAGE_WINDOW / 60:.2f} minutes)"
            f"\n\tPercent Change Threshold: {config.PCT_CHANGE_THRESHOLD}"
        )
    )

    global data_points_processed
    monitor = MovingAverageMonitor()

    try:
        monitor.initialize_writer(config.OUTPUT_FILE)
        reader = SpotRateReader().jsonlines_reader(input_file)
        for obj in reader:
            try:
                data = CurrencyConversionRate.parse_obj(obj)
                monitor.process_new_rate(data)
                data_points_processed += 1
            except ValidationError as e:
                logger.warning(e)

        monitor.terminate_writer()
    except FileNotFoundError as e:
        logger.error(e)
        raise e
    except InvalidLineError as e:
        logger.error(e)
        raise e
    except SpotRateWriterError as e:  # pragma: no cover
        logger.error(e)
        raise e


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    logger.info(f"{data_points_processed} data points processed in {end_time - start_time:.2f} seconds")
