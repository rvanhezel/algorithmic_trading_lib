from src.readers.abstract_apis import AbstractMarketDataAPI
from src.readers.rest_api import RestAPI
import pandas as pd
import logging
from src.execution.configuration import Configuration
import os
import datetime as dt
from src.parsers.time_series_json_parsers import AlphaVantageTimeSeriesJSONParser
from src.data_structures.time_series_inputs import TimeSeriesInputs, AlphaVantageTimeSeriesInputs
from typing import Optional, Any
from src.utilities.period import Period
from src.utilities.utils import calc_intraday_time_points, shift_date_by_period


class AlphaVantageAPI(AbstractMarketDataAPI, RestAPI):
    """
    Interface for market data providers.

    Provides methods for connecting to a data source, subscribing to tickers,
    and retrieving the latest market data.
    """

    def __init__(self):
        RestAPI.__init__(self)
        self.base_url = "https://www.alphavantage.co/query?"
        self.access_key = os.environ.get('ALPHA_VANTAGE_KEY', 'WRONG-KEY')

    def get_price(self, ticker: str) -> float:
        """
        Retrieve the latest market price for the given ticker.
        I think this should be function=REALTIME_BULK_QUOTES in the API -> Premium service. 
        We use GLOBAL_QUOTE instead, like for quote.

        :param ticker: The ticker symbol to fetch data for.
        :return: A dictionary containing market data.
        """
        price = self.get(params={"function": "GLOBAL_QUOTE", 
                                 "symbol": ticker,
                                 "apikey": self.access_key})	
        return float(price['Global Quote']['05. price'])

    def get_quote(self, ticker: str) -> dict:
        """
        Retrieve the latest historical eod quote for the given ticker.

        :param ticker: The ticker symbol to fetch data for.
        :return: A dictionary containing quote data.
        """
        return {'close': self.get_price(ticker)}
    

    def get_historical_prices(self, 
                              symbol: str, 
                              interval: Period, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              number_points: Optional[int] = None,
                              timezone: str = None) -> pd.DataFrame:
        # to do - set correct timezone in returned data
        time_series_params={"function": None, 
                            "symbol": symbol,
                            "apikey": self.access_key,
                            "outputsize": None}
        
        if interval.units != 1 and interval.tenor != "min":
            raise ValueError("Historical data frequency only available 1d/1w/1m for Alpha Vantage")
        
        if number_points is None:
            time_series_max_start_date = shift_date_by_period(Period("20Y"), end_date, "-")
            if start_date < time_series_max_start_date:
                msg = f"Historical data horizon from {start_date} to {end_date} is not available. Period is too long"
                raise ValueError(msg)
        
        # outputsize calc. Should be compact if < 100 else full. full has data fore 20 years
        time_points_in_interval = calc_intraday_time_points(str(interval), start_date, end_date) if number_points is None else number_points
        if time_points_in_interval > 100:
            time_series_params["outputsize"] = "full"
        elif time_points_in_interval <= 100:	
            time_series_params["outputsize"] = "compact"
        else:
            raise ValueError("Problem with historical data query")
        
        if interval.tenor == "min":
            time_series_params["function"] = 'TIME_SERIES_INTRADAY'
            time_series_params["interval"] = str(interval)

            # AlphaVantage only has at most the last 30 days of intraday data available
            max_points_available = 60 / interval.units * 24 * 30
            
            if time_points_in_interval > max_points_available:
                msg = f"Historical data from {start_date} to {end_date} not available with"
                msg += f" a {interval} frequency with Alpha Vantage. Too many points"
                raise ValueError(msg)
            
            elif 100 < time_points_in_interval <= max_points_available:
                time_series_params["outputsize"] = "full"
            elif time_points_in_interval <= 100:	
                time_series_params["outputsize"] = "compact"
            else:
                raise ValueError("Problem with historical data query")
                
        elif interval.tenor.upper() == "D":
            time_series_params["function"] = 'TIME_SERIES_DAILY'
            time_series_params["interval"] = "1d"
        elif interval.tenor == "W":
            time_series_params["function"] = 'TIME_SERIES_WEEKLY'
            time_series_params["interval"] = "1w"
        elif interval.tenor == "M":
            time_series_params["function"] = 'TIME_SERIES_MONTHLY'
            time_series_params["interval"] = "1m"
        else:
            raise ValueError("Only D/W/M supported for Alpha Vantage time series")
        
        time_series = self.get(params=time_series_params)	
        return AlphaVantageTimeSeriesJSONParser.parse(time_series).iloc[:number_points] \
            if number_points is not None else AlphaVantageTimeSeriesJSONParser.parse(time_series)

    
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


    def get_real_time_price(self, ticker: str) -> pd.DataFrame:
        """
        Fetch real-time price for a given symbol.

        :param symbol: The stock/crypto/forex symbol.
        :return: Real-time price as a dictionary.
        """
        price = self.get(params={"function": "GLOBAL_QUOTE", 
                                 "symbol": ticker,
                                 "apikey": self.access_key})	
        return float(price['Global Quote']['05. price'])

    def get_crypto_prices(self, symbol: str, interval: str) -> pd.DataFrame:
        """
        Fetch cryptocurrency prices for a given symbol.

        :param symbol: The cryptocurrency symbol (e.g., 'BTC/USD').
        :param interval: The data interval (e.g., 'daily').
        :return: Cryptocurrency prices as a dictionary.
        """
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": "USD"
        }
        return self._make_request(params)

    def get_forex_prices(self, currency_pair: str, interval: str) -> pd.DataFrame:
        """
        Fetch forex currency pair prices.

        :param currency_pair: The forex pair (e.g., 'EUR/USD').
        :param interval: The data interval (e.g., '5min').
        :return: Forex prices as a dictionary.
        """
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": currency_pair.split('/')[0],
            "to_symbol": currency_pair.split('/')[1],
            "interval": interval
        }
        return self._make_request(params)

    def get_technical_indicator(self, symbol: str, indicator: str, interval: str, **kwargs: Any) -> pd.DataFrame:
        """
        Fetch a specific technical indicator for a given symbol.

        :param symbol: The stock/crypto/forex symbol.
        :param indicator: The indicator name (e.g., 'SMA', 'EMA').
        :param interval: The data interval (e.g., '1min', 'daily').
        :param kwargs: Additional parameters for the indicator (e.g., time period).
        :return: Technical indicator data as a dictionary.
        """
        params = {
            "function": indicator,
            "symbol": symbol,
            "interval": interval
        }
        params.update(kwargs)
        return self._make_request(params)

    def get_company_profile(self, symbol: str) -> None:
        """
        Fetch the company profile for a given symbol.
        (Not supported by Alpha Vantage.)

        :param symbol: The stock symbol.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Alpha Vantage does not provide company profile data.")

    def get_financial_statements(self, symbol: str, statement_type: str) -> dict[str, Any]:
        """
        Fetch financial statements for a given symbol.

        :param symbol: The stock symbol.
        :param statement_type: The type of statement (e.g., 'income', 'balance_sheet').
        :return: Financial statement data as a dictionary.
        """
        params = {
            "function": statement_type,
            "symbol": symbol
        }
        return self._make_request(params)

    def get_earning(self, symbol: str, statement_type: str) -> dict[str, Any]:
        """
        Fetch earnings reports for a given symbol.

        :param symbol: The stock symbol.
        :param statement_type: The type of earnings report (e.g., 'quarterly').
        :return: Earnings report data as a dictionary.
        """
        params = {
            "function": "EARNINGS",
            "symbol": symbol
        }
        return self._make_request(params)

    def get_news(self, 
                 ticker: str,
                 start_date: Optional[pd.Timestamp] = None, 
                 end_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """
        Fetch news articles for a given symbol.
        (Not supported by Alpha Vantage.)

        :param symbol: The stock symbol.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        fmt_start_date = start_date.strftime('%Y%m%dT%H%M') if start_date is not None else None
        fmt_end_date = end_date.strftime('%Y%m%dT%H%M') if end_date is not None else None

        data = self.get(params={"function": "NEWS_SENTIMENT", 
                                 "symbol": ticker,
                                 "apikey": self.access_key,
                                 "time_from": fmt_start_date,
                                 "time_to": fmt_end_date})
        df = pd.DataFrame(data['feed'])
        df['time_published'] = pd.to_datetime(df['time_published'], format='%Y%m%dT%H%M%S')
        return df

    def get_sentiment(self, symbol: str) -> None:
        """
        Fetch sentiment analysis for a given symbol.
        (Not supported by Alpha Vantage.)

        :param symbol: The stock symbol.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Alpha Vantage does not provide sentiment data.")

    def get_economic_indicator(self, indicator: str) -> None:
        """
        Fetch economic indicators.
        (Not supported by Alpha Vantage.)

        :param indicator: The economic indicator name.
        :raises NotImplementedError: Always raises as this feature is unsupported.
        """
        raise NotImplementedError("Alpha Vantage does not provide economic indicator data.")