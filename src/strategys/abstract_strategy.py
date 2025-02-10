from abc import ABC, abstractmethod
from src.utilities.enums import Signal
from src.readers.abstract_apis import AbstractMarketDataAPI
from src.services.market_data_service import MarketDataService
from src.execution.configuration import Configuration


class AbstractStrategy(ABC):
    """
    Abstract interface for trading strategies.

    Defines methods for processing market data and generating trade signals.
    """
    @staticmethod
    @abstractmethod
    def generate_signals(mkdata_service: MarketDataService, ticker: list[str], cfg: Configuration) -> dict[str, Signal]:        
        """
        Generate a trade signal based on the provided market data.

        :param mkdata_api: Market data API instance
        :param ticker: Ticker symbol
        :return: dict of Signals
        """
        pass
