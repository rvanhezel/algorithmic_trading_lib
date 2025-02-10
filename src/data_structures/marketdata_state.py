import pandas as pd
from src.readers.abstract_apis import AbstractMarketDataAPI
from src.execution.configuration import Configuration
from src.utilities.utils import calc_intraday_time_points, timezone_from_calendar, shift_date_by_period
import time
import logging
import pytz


class MarketDataState:
    """This class represents a state management system for market data, providing methods to manage APIs, 
        retrieve historical and intraday data, and update the state dynamically. It encapsulates the complexities 
        of interacting with multiple APIs and managing data retrieval in a structured and modular way.

        Main responsibility: API management.

        Notes: The MarketDataService layer controls the logic
    """

    def __init__(self):
        self._apis: dict[str, AbstractMarketDataAPI] = {}
        self._market_data = {}

    @property
    def apis(self) -> None:
        return self._apis

    @apis.setter
    def apis(self, other) -> None:
        self._apis = other

    @property
    def market_data(self):
        return self._market_data
    
    @market_data.setter
    def market_data(self, other) -> None:
        self._market_data = other

    def add_apis(self, apis: dict[str, AbstractMarketDataAPI]) -> None:
        for api_name, api_fun in apis.items():
            self.apis[api_name] = api_fun

    def populate_historical_data(self, tickers: list[str], cfg: Configuration) -> None:
        for api_name, api in self.apis.items(): 
            current_api_mkdata = {}
            for ticker in tickers:

                if cfg.market_data_api == "twelve_data":
                    current_api_mkdata[ticker] = api.get_historical_prices(
                        symbol=ticker,
                        interval=cfg.historical_data_frequency,
                        start_date= shift_date_by_period(cfg.historical_data_horizon, pd.Timestamp.today(), "-"),
                        end_date=pd.Timestamp.today(),
                        timezone=timezone_from_calendar(cfg.market)
                        )
                elif cfg.market_data_api == "alpha_vantage":
                    current_api_mkdata[ticker] = api.get_historical_prices(
                        symbol=ticker,
                        interval=cfg.historical_data_frequency,
                        start_date= shift_date_by_period(cfg.historical_data_horizon, pd.Timestamp.today(), "-"),
                        end_date=pd.Timestamp.today(),
                        timezone=timezone_from_calendar(cfg.market)
                        )
                else:
                    raise ValueError("Market data API not recognized")
            
            self._market_data[api_name] = current_api_mkdata

    def populate_intraday_data(self, tickers: list[str], cfg: Configuration) -> None:
        timezone=timezone_from_calendar(cfg.market)
        now = pd.Timestamp.now(tz=timezone) 
        market_open = pd.Timestamp(now.year, now.month, now.day, 9, 30, tz=timezone)
        self._populate_intraday_between_dates(tickers, cfg, market_open, now)

    def populate_state(self, cfg: Configuration):
        """
        Appends the latest intraday candles to the existing state. Adds datapoints
        between the last existing timestamp in the state and the current time.
        """
        logging.info(f"Populating market data state")

        #Get existing tickers in state
        tickers = []
        for api_mapping in self._market_data.values():
            for ticker in api_mapping.keys():
                tickers.append(ticker)
        
        # assumes all data has the same last timestamp
        latest_timestamp = self._market_data.get(list(self._market_data.keys())[0]).get(tickers[0]).index[0]

        now = pd.Timestamp.now(tz=timezone_from_calendar(cfg.market))
        time_elapsed = (now - latest_timestamp).seconds
        time_step = pd.Timedelta(str(cfg.intraday_interval)).seconds

        if time_elapsed < time_step:
            time_to_sleep = time_step - time_elapsed
            message = f"MarketDataState: Current timestamp: {now}."
            message += f" Last market data timestamp: {latest_timestamp}."
            message += f" Going to sleep for: {time_to_sleep} seconds"
            logging.warning(message)
            time.sleep(time_to_sleep)

        now = pd.Timestamp.now(tz=timezone_from_calendar(cfg.market))
        self._populate_intraday_between_dates(tickers, cfg, latest_timestamp, now)
        logging.debug("Market data state updated")

    def _populate_intraday_between_dates(self, 
                                          tickers: list[str], 
                                          cfg: Configuration,
                                          start_date: pd.Timestamp,
                                          end_date: pd.Timestamp) -> None:
        """Appends time series data to the market state between and including 
        start and end timestamps.
        """
        # Calculate how many intraday datapoints we need for given time interval
        points_for_time_series = calc_intraday_time_points(str(cfg.intraday_interval),
                                                           start_date,
                                                           end_date)

        if points_for_time_series <=0:
            logging.warning(f"Tryign to populate market state with start date > end date. {start_date} > {end_date}")
            return None

        for api_name, api in self.apis.items():

            if api_name in self._market_data:

                current_api_mkdata = {}
                for ticker in tickers:

                    if ticker in self._market_data[api_name]:
                        current_data = self._market_data[api_name][ticker]
                        
                        new_data = api.get_intraday_prices(
                            ticker, 
                            cfg.intraday_interval,
                            points_for_time_series,
                            timezone=timezone_from_calendar(cfg.market)
                            )

                        current_api_mkdata[ticker] = pd.concat([current_data, new_data], axis=0)
                        current_api_mkdata[ticker].sort_index(ascending=False, inplace=True)

                    else:
                        current_api_mkdata[ticker] = api.get_time_series(ticker, cfg)

                self._market_data[api_name] = current_api_mkdata

            else:
                current_api_mkdata = {}
                for ticker in tickers:

                    current_api_mkdata[ticker] = api.get_intraday_prices(
                        ticker,
                        cfg.intraday_interval,
                        points_for_time_series,
                        timezone=timezone_from_calendar(cfg.market)
                        )
                
                self._market_data[api_name] = current_api_mkdata




    

    