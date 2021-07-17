from datetime import datetime
from pydantic import BaseModel, validator

UnixTimestamp = float


class CurrencyConversionRate(BaseModel):
    """Class for representing a single currency conversion rate data point.

    This class uses pydantic BaseModel for enforcing data type adherence,
    and validates unix timestamp upon instantiation.

    Example:
        obj = { "timestamp": 1554933784.023, "currencyPair": "CNYAUD", "rate": 0.39281 }
        data = CurrencyConversionRate.parse_obj(obj).

    Throws:
        ValidationError: the data is incomplete (missing attributes), or the timestamp is invalid.
    """
    timestamp: UnixTimestamp
    currencyPair: str
    rate: float

    @validator('timestamp')
    def check_timestamp(cls, v: float):
        """Validate timestamp before instantiating this object"""
        try:
            datetime.utcfromtimestamp(v)
            return v
        except Exception as e:
            raise ValueError('timestamp must be Unix Timestamp') from e

    def get_datetime(self) -> datetime:
        """Returns the datetime object of the timestamp."""
        return datetime.utcfromtimestamp(self.timestamp)
