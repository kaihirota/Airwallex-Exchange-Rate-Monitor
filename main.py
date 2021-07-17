from reader import SpotRateReader
from currency_conversion_rate import CurrencyConversionRate

if __name__ == '__main__':
    reader = SpotRateReader.jsonlines_reader("example/input1.jsonl")
    for obj in reader:
        data = CurrencyConversionRate.parse_obj(obj)
        print(data, type(data))