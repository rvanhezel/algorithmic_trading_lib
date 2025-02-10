import datetime as dt
from src.readers.abstract_apis import AbstractMarketDataAPI
from twelvedata import exceptions
from twelvedata import TDClient
import pandas as pd
import logging
from src.execution.configuration import Configuration
import os
from src.parsers.time_series_json_parsers import TwelveDataTimeSeriesJSONParser
from src.data_structures.time_series_inputs import TimeSeriesInputs, TwelveDataTimeSeriesInputs
from src.utilities.utils import split_tenor_string
from typing import Optional, Any
from src.utilities.period import Period


class TwelveDataAPI(AbstractMarketDataAPI):

    def __init__(self):
        """
        Initialize the Twelve Data API with their Python SDK client.        
        """
        self.api_key = os.environ.get('TWELVE_DATA_KEY', 'WRONG-KEY')
        self._connect()

    def _connect(self) -> None:
        """Establish a connection to Twelve Data API"""
        logging.debug("Connecting to Twelve Data API")
        try:
            self.client_api = TDClient(apikey=self.api_key)
        except Exception as err:
            logging.error(f"Error connecting to Twelve Data: {err}")
            raise exceptions.TwelveDataError("Error connecting to Twelve Data")
        
        logging.info("Successfully connected to Twelve Data")

    def get_historical_prices(self, 
                              symbol: str, 
                              interval: Period, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              number_points: Optional[int] = None,
                              timezone: str = None) -> pd.DataFrame:
        if interval.tenor == "d":
            interval = str(interval.units) + "day"

        data = self.client_api.time_series(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            outputsize=number_points,
            timezone=timezone
        ).as_json()

        return TwelveDataTimeSeriesJSONParser.parse(data, timezone)

    def get_intraday_prices(self,
                            symbol: str, 
                            interval: Period,
                            number_points: int,
                            timezone: str = None) -> pd.DataFrame:
        """
        Fetch intraday prices for a given symbol.
        
        :param symbol: The stock/crypto/forex symbol.
        :param interval: The data interval (e.g., '1min').
        :return: Intraday prices as a dictionary.
        """
        return self.get_historical_prices(symbol, interval, None, None, number_points, timezone)

    def get_real_time_price(self, symbol: str) -> float:
        """
        Fetch real-time price for a given symbol.
        
        :param symbol: The stock/crypto/forex symbol.
        :return: Real-time price as a dictionary.
        """
        price = self.client_api.price(symbol=symbol).as_json()
        return float(price['price'])
    
    def quote(self, symbol, interval):
        return self.client_api.quote(symbol=symbol, interval=interval).as_json()

    def get_crypto_prices(self, symbol: str, interval: str) -> pd.DataFrame:
        """
        Fetch cryptocurrency prices for a given symbol.
        
        :param symbol: The cryptocurrency symbol (e.g., 'BTC/USD').
        :param interval: The data interval (e.g., '1min', '1day').
        :return: Cryptocurrency prices as a dictionary.
        """
        return self.get_historical_prices(symbol, interval, None, None)

    def get_forex_prices(self, currency_pair: str, interval: str) -> pd.DataFrame:
        """
        Fetch forex currency pair prices.
        
        :param currency_pair: The forex pair (e.g., 'EUR/USD').
        :param interval: The data interval (e.g., '1min', '1day').
        :return: Forex prices as a dictionary.
        """
        return self.get_historical_prices(currency_pair, interval, None, None)

    def get_technical_indicator(self, symbol: str, indicator: str, interval: str, **kwargs: Any) -> dict[str, Any]:
        """
        Fetch a specific technical indicator for a given symbol.
        
        :param symbol: The stock/crypto/forex symbol.
        :param indicator: The indicator name (e.g., 'sma', 'rsi').
        :param interval: The data interval (e.g., '1min', '1day').
        :param kwargs: Additional parameters for the indicator (e.g., period).
        :return: Technical indicator data as a dictionary.
        """
        return self.client_api.indicator(
            symbol=symbol,
            interval=interval,
            indicator=indicator,
            **kwargs
        ).as_json()

    def get_company_profile(self, symbol: str) -> dict[str, Any]:
        """
        Fetch the company profile for a given symbol.
        
        :param symbol: The stock symbol.
        :return: Company profile as a dictionary.
        """
        return self.client_api.profile(symbol=symbol).as_json()

    def get_financial_statements(self, symbol: str, statement_type: str) -> dict[str, Any]:
        """
        Fetch financial statements for a given symbol.
        
        :param symbol: The stock symbol.
        :param statement_type: The type of statement (e.g., 'income', 'balance_sheet').
        :return: Financial statement data as a dictionary.
        """
        return self.client_api.financials(symbol=symbol, statement_type=statement_type).as_json()

    def get_earning(self, symbol: str, statement_type: str) -> None:
        """
        Fetch earnings reports.
        (Not supported by Twelve Data.)

        :param symbol: The stock symbol.
        :param statement_type: The type of statement (e.g., 'earnings').
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Twelve Data does not provide earnings data.")

    def get_news(self, symbol: str) -> None:
        """
        Fetch news articles for a given symbol.
        (Not supported by Twelve Data.)

        :param symbol: The stock symbol.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Twelve Data does not provide news data.")

    def get_sentiment(self, symbol: str) -> None:
        """
        Fetch sentiment analysis for a given symbol.
        (Not supported by Twelve Data.)

        :param symbol: The stock symbol.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Twelve Data does not provide sentiment data.")

    def get_economic_indicator(self, indicator: str) -> None:
        """
        Fetch economic indicators.
        (Not supported by Twelve Data.)

        :param indicator: The economic indicator name.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Twelve Data does not provide economic indicator data.")
