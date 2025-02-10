from dataclasses import dataclass
from datetime import date
from src.execution.configuration import Configuration


@dataclass
class TimeSeriesInputs:
    """
    A dataclass to hold inputs for time series data retrieval.

    Attributes:
        ticker (str): The ticker symbol of the asset.
        time_interval (str): The time interval for the data (e.g., '1d', '1wk', '1mo').
    """
    ticker: str = None
    time_interval: str = None
    output_size: int|str = None # twelve data. Default is 30. Ranges from 1 to 5000
    # output_size: str = None # alpha vantage. full or compact
    period: str = None # alpha vantage 1d/1w/1m


@dataclass
class TwelveDataTimeSeriesInputs(TimeSeriesInputs):

    """param: time_interval. 1m,5m,15m,30m,45m,1h,2h,4h,1day,1week,1month
    :param output_size. Default is 30. Ranges from 1 to 5000

    Notes
    -----
    The time series fun of the API converts "1d, 1w, 1y" to the TwelveData format"""
    output_size: int = None

    def set(self, ticker:str, cfg: Configuration) -> None:
        super().set(ticker, cfg)
        self.output_size = cfg.output_size


@dataclass
class AlphaVantageTimeSeriesInputs(TimeSeriesInputs):
    """
    :param time_interval: The time interval for the data.
                            Possible: 1m,5m,15m,30m,60m
    :param period: Optional. The period for the time series data.
            Possible: 1d,1w,1m
    """
    output_size: str = None
    period: str = None

    def set(self, ticker:str, cfg: Configuration) -> None:
        super().set(self, ticker, cfg)
        self.output_size = cfg.output_size
        self.period = cfg.period



