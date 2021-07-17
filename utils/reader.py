import os

import jsonlines
from jsonlines.jsonlines import Reader
from loguru import logger


@logger.catch
class SpotRateReader:
    """Class for reading jsonlines file.

    Throws:
        FileNotFoundError
    """

    @staticmethod
    def jsonlines_reader(path: str) -> Reader:
        """Returns an iterable wrapper for the jsonlines file."""

        if not os.path.exists(path):
            raise FileNotFoundError(f"The input file does not exist: {path}")

        return jsonlines.open(path)
