from abc import ABC, abstractmethod
from src.execution.configuration import Configuration
from src.data_structures.order import Order
from src.data_structures.position import Position
import logging
from src.utilities.enums import OrderType
from src.utilities.enums import Signal
import pandas as pd
from src.data_structures.time_series_inputs import TimeSeriesInputs
from typing import Optional
from src.utilities.period import Period


class AbstractBrokerAPI(ABC):
    __slots__ = ('client_api')

    @abstractmethod
    def connect(self, config: Configuration) -> None:
        pass

    @abstractmethod
    def place_market_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def place_limit_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def get_all_positions(self) -> list[Position]:
        pass

    @abstractmethod
    def get_cash(self) -> float:
        pass

    @abstractmethod
    def get_equity(self) -> float:
        pass

    @abstractmethod
    def close_all_positions(self) -> None:
        pass

    @abstractmethod
    def close_positions(self, ticker: list[str]) -> None:
        pass

    def place_orders(self, orders: list[Order]) -> None:
        """
        Place a trade order.

        :param order: The order object containing trade details.
        :param state: The portfolio state to update upon successful order placement.
        """
        for order in orders:
            if order.direction == Signal.HOLD:
                logging.info(f"Order direction is HOLD, no order placed")
                return None
            
            if order.type == OrderType.MARKET:
                self.place_market_order(order)
            elif order.type == OrderType.LIMIT:
                self.place_limit_order(order)
            else:
                raise ValueError(f"Unsupported order type: {order.order_type}")
        

class AbstractMarketDataAPI(ABC):
    """
    Reader for market data providers.

    Provides methods for connecting to a data source, subscribing to tickers,
    and retrieving the latest market data.
    """
    __slots__ = ('api_key')

    # Core market data
    @abstractmethod
    def get_historical_prices(self, 
                              symbol: str, 
                              interval: Period, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              number_points: Optional[int] = None,
                              timezone: str = None) -> pd.DataFrame:
        """Fetch historical prices for a given symbol.
        :param number_points: Needed for intraday data"""
        pass

    @abstractmethod
    def get_intraday_prices(self,
                            symbol: str, 
                            interval: Period,
                            number_points: int,
                            timezone: str = None) -> pd.DataFrame:
        """Fetch intraday prices for a given symbol."""
        pass

    @abstractmethod
    def get_real_time_price(self, symbol: str) -> float:
        """Fetch real-time price for a given symbol."""
        pass

    # FX, Crypto
    @abstractmethod
    def get_crypto_prices(self, symbol: str, interval: str) -> pd.DataFrame:
        """Fetch cryptocurrency prices."""
        pass

    @abstractmethod
    def get_forex_prices(self, currency_pair: str, interval: str) -> pd.DataFrame:
        """Fetch forex currency pair prices."""
        pass

    # Technical indicators
    @abstractmethod
    def get_technical_indicator(self, symbol: str, indicator: str, interval: str, **kwargs):
        """Fetch a specific technical indicator for a given symbol.
        (SMA, EMA, WMA, VWAP, MACD)"""
        pass

    # Fundamental data
    @abstractmethod
    def get_company_profile(self, symbol: str):
        """Fetch company profile for a given symbol."""
        pass

    @abstractmethod
    def get_financial_statements(self, symbol: str, statement_type: str):
        """Fetch financial statements (income, balance sheet, cash flow)."""
        pass

    @abstractmethod
    def get_earning(self, symbol: str, statement_type: str):
        """Fetch earnings reports"""
        pass

    # News & sentiment
    @abstractmethod
    def get_news(self, 
                 symbol: str,
                 start_date: Optional[pd.Timestamp] = None, 
                 end_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """Fetch news articles for a given symbol."""
        pass

    @abstractmethod
    def get_sentiment(self, symbol: str):
        """Fetch sentiment analysis for a given symbol."""
        pass   

    # Economic indicators
    @abstractmethod
    def get_economic_indicator(self, indicator: str):
        """Fetch economic indicators (GDP, CPI, Inflation, Retail sales, unemployment)."""
        pass