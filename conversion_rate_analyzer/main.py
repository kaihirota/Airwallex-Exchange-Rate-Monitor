from pathlib import Path
import sys
import time

from loguru import logger
from pydantic.error_wrappers import ValidationError

PROJECT_ROOT_DIR = str(Path(__file__).parent.parent)
if PROJECT_ROOT_DIR not in sys.path:  # pragma: no cover
    sys.path.append(PROJECT_ROOT_DIR)

from conversion_rate_analyzer.config import MOVING_AVERAGE_WINDOW, PCT_CHANGE_THRESHOLD
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.moving_average import MovingAverageQueue
from conversion_rate_analyzer.utils.reader import SpotRateReader

data_points_processed = 0


def main():
    if len(sys.argv) < 2:
        e = IndexError("Supply the input file path as an argument: python main.py input.jsonl")
        logger.warning(e)
        # sys.exit(1)
        raise e

    input_file = sys.argv[1]
    logger.info(
        (
            "Program starting with parameters:"
            f"\n\tInput File: {input_file}"
            f"\n\tMoving Average Window Size: {MOVING_AVERAGE_WINDOW} ({MOVING_AVERAGE_WINDOW / 60:.2f} minutes)"
            f"\n\tPercent Change Threshold: {PCT_CHANGE_THRESHOLD}"
        )
    )

    global data_points_processed
    queue = MovingAverageQueue()

    try:
        reader = SpotRateReader().jsonlines_reader(input_file)
        for obj in reader:
            try:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)
                data_points_processed += 1
            except ValidationError as e:
                logger.warning(e)
    except FileNotFoundError as e:
        logger.exception(e)
        # sys.exit(1)
        raise e


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"{data_points_processed} data points processed in {end_time - start_time:.2f} seconds")
