from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class TimeSeriesJSONParser(ABC):
    """
    Base class for parsing the JSON returned from market data API
    time series function calls.
    """
    @staticmethod
    @abstractmethod
    def parse(data: dict[str, Any]) -> pd.DataFrame:
        """
        Parses the JSON data retured an API call and return it as a DataFrame.

        Args:
            data (dict[str, any]): The JSON data to parse.

        Returns:
            pd.DataFrame: A DataFrame containing the parsed OHLCV data.
        """
        pass


class AlphaVantageTimeSeriesJSONParser(TimeSeriesJSONParser):
    """
    Parser for Alpha Vantage API data.
    """
    @staticmethod
    def parse(data: dict[str, Any]) -> pd.DataFrame:
        """
        Parses Alpha Vantage JSON data.

        Args:
            data (dict[str, Any]): The JSON data from Alpha Vantage API.

        Returns:
            pd.DataFrame: A DataFrame with OHLCV data.
        """
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break

        df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.astype(float) 
        df = df.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            }
        )
        return df[["Open", "High", "Low", "Close", "Volume"]]


class yFinanceTimeSeriesJSONParser(TimeSeriesJSONParser):
    """
    Parser for yFinance  - Yahoo Finance API time series data.
    """
    @staticmethod
    def parse(data: dict[str, Any]) -> pd.DataFrame:
        """
        Parses Yahoo Finance JSON data.

        Args:
            data (Dict[str, Any]): The JSON data from Yahoo Finance API.

        Returns:
            pd.DataFrame: A DataFrame with OHLCV data.
        """
        raise NotImplementedError("yFinance Yahoo Finance API parser not yet implemented")
    

class TwelveDataTimeSeriesJSONParser(TimeSeriesJSONParser):
    """
    Parser for Twelve Data API time series data.
    """
    @staticmethod
    def parse(data: dict[str, Any], timezone: str) -> pd.DataFrame:
        # time_series = data["Time Series (Daily)"]
        # df = pd.DataFrame.from_dict(time_series, orient="index")
        # df.index = pd.to_datetime(df.index)
        # df = df.astype(float) 
        # df = df.rename(
        #     columns={
        #         "1. open": "Open",
        #         "2. high": "High",
        #         "3. low": "Low",
        #         "4. close": "Close",
        #         "5. volume": "Volume",
        #     }
        # )
        # return df[["Open", "High", "Low", "Close", "Volume"]]

        df = pd.DataFrame(data)
        df.index = pd.to_datetime(df['datetime']).dt.tz_localize(timezone)
        df.pop('datetime')
        return df