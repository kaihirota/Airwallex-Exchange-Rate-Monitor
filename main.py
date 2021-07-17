import sys

from loguru import logger

from config import MOVING_AVERAGE_WINDOW, PCT_CHANGE_THRESHOLD
from models.currency_conversion_rate import CurrencyConversionRate
from moving_average import MovingAverageQueue
from utils.reader import SpotRateReader
from pydantic.error_wrappers import ValidationError


@logger.catch
def main():
    if len(sys.argv) < 2:
        logger.warning("Supply the input file path as an argument: python main.py input.jsonl")
        sys.exit(-1)

    input_file = sys.argv[1]
    logger.info(
        (
            "Program starting with parameters:"
            f"\n\tInput File: {input_file}"
            f"\n\tMoving Average Window Size: {MOVING_AVERAGE_WINDOW} ({MOVING_AVERAGE_WINDOW / 60:.2f} minutes)"
            f"\n\tPercent Change Threshold: {PCT_CHANGE_THRESHOLD}"
        )
    )

    queue = MovingAverageQueue()

    try:
        reader = SpotRateReader().jsonlines_reader(input_file)
        for obj in reader:
            try:
                data = CurrencyConversionRate.parse_obj(obj)
                queue.process_new_rate(data)
            except ValidationError as e:
                logger.warning(e)
    except FileNotFoundError as e:
        logger.exception(e)
        sys.exit(-1)


if __name__ == '__main__':
    main()
