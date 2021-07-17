import jsonlines
from jsonlines.jsonlines import Reader


class SpotRateReader:
    @staticmethod
    def jsonlines_reader(path: str) -> Reader:
        return jsonlines.open(path)
