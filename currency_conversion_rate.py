from datetime import datetime
from pydantic import BaseModel, ValidationError, validator

UnixTimestamp = float


class CurrencyConversionRate(BaseModel):
    """Class for representing a single currency conversion rate data point."""
    timestamp: UnixTimestamp
    currencyPair: str
    rate: float

    def get_datetime(self) -> datetime:
        return datetime.utcfromtimestamp(self.timestamp)

    @validator('timestamp')
    def timestamp_must_be_unix(cls, v):
        try:
            datetime.utcfromtimestamp(v)
            return v
        except Exception as e:
            raise ValueError('timestamp must be Unix Timestamp')
