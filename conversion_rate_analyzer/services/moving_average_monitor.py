from queue import PriorityQueue

from loguru import logger

from conversion_rate_analyzer import config
from conversion_rate_analyzer.models.currency_conversion_rate import CurrencyConversionRate
from conversion_rate_analyzer.utils.exceptions import SpotRateWriterError
from conversion_rate_analyzer.utils.writer import SpotRateWriter


class MovingAverageMonitor:
    """Singleton object for storing the latest conversion rates and keeping the moving average updated.

    This is a singleton object for storing the latest n conversion rates for
    all the currency pairs, where n is MOVING_AVERAGE_WINDOW as specified in the config file.
    If multiple instantiation is attempted, reference to the existing instance will be returned.

    For each currency pair, this object creates a queue with finite capacity
    to hold the latest n conversion rates (specified by MOVING_AVERAGE_WINDOW in the config file).

    By using a PriorityQueue, even if conversion rates are received out-of-order,
    the accuracy of moving average will not be lost as items will be dequeued by timestamp priority.

    Throws:
        KeyError: Currency pair does not exist.
        SpotRateWriterError:
            Attempt made to write without initializing the jsonline writer,
            or the output file has been removed before closing.
    """

    instance = None

    def __new__(cls):
        """Called implicitly before __init__(self)."""

        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.known_currency_pairs = set()

        # queue of conversion rates over the specified moving average window
        self.conversion_rates_queue = {}

        # sum of the conversion rates contained in `self.conversion_rates` and the current queue size
        self.conversion_rates_sum_count = {}

        self.jsonline_writer = None

    def initialize_writer(self, path: str):
        if self.jsonline_writer:
            self.jsonline_writer.close()

        logger.info(f"Initializing jsonline writer with output path: {path}.")
        self.jsonline_writer = SpotRateWriter(path)

    def terminate_writer(self):
        logger.info(f"Terminating jsonline writer...")
        try:
            self.jsonline_writer.close()
        except SpotRateWriterError as e:
            logger.exception(e)
            raise e

    def process_new_rate(self, data: CurrencyConversionRate):
        """Process new conversion rate data."""
        if not self.jsonline_writer:
            e = SpotRateWriterError("Jsonline writer not initialized")
            logger.error(e)
            raise e

        if data.currencyPair not in self.known_currency_pairs:
            self.known_currency_pairs.add(data.currencyPair)
            self.conversion_rates_queue[data.currencyPair] = PriorityQueue(maxsize=config.MOVING_AVERAGE_WINDOW)
            self.conversion_rates_queue[data.currencyPair].put((data.timestamp, data.rate))
            self.conversion_rates_sum_count[data.currencyPair] = (data.rate, 1)
        else:
            # calculate percentage difference between the new conversion rate and the average rate
            total, count = self.conversion_rates_sum_count[data.currencyPair]
            current_avg_rate = self.get_current_average_rate(data.currencyPair)
            pct_change = (data.rate - current_avg_rate) / current_avg_rate

            if pct_change >= config.PCT_CHANGE_THRESHOLD:
                if config.VERBOSE:
                    self.jsonline_writer.write(data, current_avg_rate, pct_change)
                else:
                    self.jsonline_writer.write(data)

                logger.info(
                    (
                        f"Significant rate change (>= {config.PCT_CHANGE_THRESHOLD}) recorded."
                        f"\n\tCurrency pair : {data.currencyPair}"
                        f"\n\tAverage rate  : {current_avg_rate:.6f}"
                        f"\n\tNew spot rate : {data.rate:.6f}"
                        f"\n\tPercent change: {pct_change * 100:.2f}%"
                    )
                )

            # update queue, total, and count
            if self.conversion_rates_queue[data.currencyPair].full():
                _, expired_rate = self.conversion_rates_queue[data.currencyPair].get()
                self.conversion_rates_sum_count[data.currencyPair] = (total - expired_rate + data.rate, count)
            else:
                self.conversion_rates_sum_count[data.currencyPair] = (total + data.rate, count + 1)

            self.conversion_rates_queue[data.currencyPair].put((data.timestamp, data.rate))

    def get_current_queue_size(self, currency_pair: str) -> int:
        if self.currency_pair_exists(currency_pair):
            _, count = self.conversion_rates_sum_count[currency_pair]
            return count
        else:
            raise KeyError(f"The currency pair ({currency_pair}) does not exist")

    def get_current_average_rate(self, currency_pair: str) -> float:
        if self.currency_pair_exists(currency_pair):
            total, count = self.conversion_rates_sum_count[currency_pair]
            return total / count
        else:
            raise KeyError(f"The currency pair ({currency_pair}) does not exist")

    def get_known_currency_pairs(self) -> set:
        return self.known_currency_pairs

    def currency_pair_exists(self, currency_pair: str) -> bool:
        return currency_pair in self.known_currency_pairs
