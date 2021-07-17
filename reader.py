import os

import jsonlines
from jsonlines.jsonlines import Reader
from loguru import logger


@logger.catch
class SpotRateReader:
    @staticmethod
    def jsonlines_reader(path: str) -> Reader:
        if not os.path.exists(path):
            raise FileNotFoundError

        return jsonlines.open(path)
