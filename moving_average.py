from queue import Queue

from loguru import logger

from config import MOVING_AVERAGE_WINDOW, PCT_CHANGE_THRESHOLD
from models.currency_conversion_rate import CurrencyConversionRate

class MovingAverageQueue:
    def __init__(self):
        self.known_currency_pairs = set()

        # queue of conversion rates over the specified moving average window
        self.conversion_rates_queue = {}

        # sum of the conversion rates contained in `self.conversion_rates` and the current queue size
        self.conversion_rates_sum_count = {}

    def process_new_rate(self, data: CurrencyConversionRate):
        if data.currencyPair not in self.known_currency_pairs:
            self.known_currency_pairs.add(data.currencyPair)
            # TODO: use priority queue instead to dequeue the oldest rate even if they arrive out-of-order?
            self.conversion_rates_queue[data.currencyPair] = Queue(maxsize=MOVING_AVERAGE_WINDOW)
            self.conversion_rates_sum_count[data.currencyPair] = (data.rate, 1)
        else:
            # calculate percentage difference between the new conversion rate and the average rate
            total, count = self.conversion_rates_sum_count[data.currencyPair]
            current_average_rate = self.get_current_average_rate(data.currencyPair)
            pct_diff = (data.rate - current_average_rate) / current_average_rate

            if pct_diff >= PCT_CHANGE_THRESHOLD:
                #TODO
                logger.info(
                    (
                        f"Significant rate change (>= {PCT_CHANGE_THRESHOLD}) detected."
                        f"\n\tAverage rate: {total / count:.6f}"
                        f"\n\tNew spot rate: {data.rate:.6f}"
                        f"\n\tPercent change: {pct_diff * 100:.2f}%"
                    )
                )

            # update queue, total, and count
            if self.conversion_rates_queue[data.currencyPair].full():
                expired_rate = self.conversion_rates_queue[data.currencyPair].get_nowait()
                self.conversion_rates_sum_count[data.currencyPair] = (total - expired_rate + data.rate, count)
            else:
                self.conversion_rates_sum_count[data.currencyPair] = (total + data.rate, count + 1)

            self.conversion_rates_queue[data.currencyPair].put(data.rate)

    def get_current_queue_size(self, currency_pair: str) -> int:
        _, count = self.conversion_rates_sum_count[currency_pair]
        return count

    def get_current_average_rate(self, currency_pair: str) -> float:
        total, count = self.conversion_rates_sum_count[currency_pair]
        return total / count

    def get_known_currency_pairs(self) -> set:
        return self.known_currency_pairs

    def currency_pair_exists(self, currency_pair: str) -> bool:
        return currency_pair in self.known_currency_pairs
