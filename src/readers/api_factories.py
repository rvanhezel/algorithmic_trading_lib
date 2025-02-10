from src.readers.abstract_apis import AbstractBrokerAPI, AbstractMarketDataAPI
from src.readers.alpaca_broker_api import AlpacaAPI
from src.readers.twelvedata_mkdata_api import TwelveDataAPI
from src.readers.yfinance_mkdata_api import yFinanceAPI
from src.readers.alpha_vantage_mkdata_api import AlphaVantageAPI

class BrokerAPIFactory:

    @staticmethod
    def create_instance(api_type: str) -> AbstractBrokerAPI:
        if api_type.lower() == "alpaca":
            return AlpacaAPI()
        else:
            ValueError(f"Unsupported API type: {api_type}")	


class MarketDataAPIFactory:

    @staticmethod
    def create_instance(api_type: str) -> AbstractMarketDataAPI:
        if api_type.lower() == "twelve_data":
            return TwelveDataAPI()
        elif api_type.lower() == "yfinance":
            return yFinanceAPI()
        elif api_type.lower() == "alpha_vantage":
            return AlphaVantageAPI()
        else:
            ValueError(f"Unsupported API type: {api_type}")	