from src.readers.abstract_apis import AbstractMarketDataAPI
import pandas as pd
import logging
from src.execution.configuration import Configuration
import os
import yfinance as yf
import datetime as dt


class yFinanceAPI(AbstractMarketDataAPI):


    def connect(self, config: Configuration) -> None:
        """Establish a connection to the market data source."""
        logging.debug("No explicit connectino required with yfinance - Yahoo! Finance")

    def get_price(self, ticker: str) -> float:
        """
        Retrieve the latest market price for the given ticker. With yFinance
        this is the last close price.

        :param ticker: The ticker symbol to fetch data for.
        :return: A dictionary containing market data.
        """
        return float(yf.Ticker(ticker).history(period="1d").iloc[-1]['Close'])

    def get_quote(self, ticker: str) -> dict:
        """
        Retrieve the latest historical eod quote for the given ticker.

        :param ticker: The ticker symbol to fetch data for.
        :return: A dictionary containing quote data.
        """
        return {'close': self.get_price(ticker)}
    
    def get_time_series(self, ticker: str, time_interval: str, outputsize: int = None,
                        start_date: dt.date = None, end_date: dt.date = None,
                        period: str = None) -> pd.DataFrame:
        """
        Retrieve the latest historical time series for the given ticker.

        :param ticker: The ticker symbol to fetch data for.
        :param interval: The time interval for the data.
                        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        :param period : str
                        Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

        :param outputsize: The number of data points to retrieve.
        :return: A dictionary containing time series data.
        """
        if outputsize is not None:
            raise AttributeError("yFinance time series method doesn't take outputsize parameter.")
        
        return yf.Ticker(ticker).history(period=period, 
                                         interval=time_interval,
                                         start=dt.date.strftime(start_date, format='%Y-%m-%d') if start_date else None,
                                         end=dt.date.strftime(end_date, format='%Y-%m-%d') if end_date else None)

    
    def get_api_usage(self):
        logging.error("yFinance API does not provide usage stats")
    
    def disconnect(self):
        """Disconnect from the API"""
        logging.debug("Explicit disconnection not required for yFinance API")

    def account_details(self):
        """Get account details"""
        pass
