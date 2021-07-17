import sys
import time

from loguru import logger
from pydantic.error_wrappers import ValidationError

from config import MOVING_AVERAGE_WINDOW, PCT_CHANGE_THRESHOLD
from models.currency_conversion_rate import CurrencyConversionRate
from moving_average import MovingAverageQueue
from utils.reader import SpotRateReader

data_points_processed = 0

@logger.catch
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


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"{data_points_processed} data points processed in {end_time - start_time:.2f} seconds")
