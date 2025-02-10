from src.execution.request import ClientRequest
import logging
from src.utilities.enums import OrderType
from dotenv import load_dotenv
import os
from src.utilities.period import Period


class Configuration:

    def __init__(self, request: ClientRequest):
        config = request.config

        self.run_type = config.get('Run', 'run_type')
        self.log_level = self._configure_log(config.get('Run', 'log_level'))
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # Bot
        self.tickers = [key.strip() for key in config.get('Bot', 'tickers').split(',')]
        self.order_type = self._configure_order_type(config.get('Bot', 'order_type'))
        self.paper_trading = config.getboolean('Bot', 'paper_trading')
        self.market = config.get('Bot', 'market', fallback="NYSE")

        # Risk management
        self.position_sizing = config.getfloat('Risk', 'position_sizing')
        self.stop_loss = config.getfloat('Risk', 'stop_loss')
        self.take_profit = config.getfloat('Risk', 'take_profit')
        self.max_exposure = config.getfloat('Risk', 'max_exposure')
        
        self.limit_order_factor = config.getfloat('Bot', 'limit_order_factor', fallback=None)
        self._check_limit_bounds()

        # APIs
        self.market_data_api = config.get('APIs', 'market_data_api')
        self.broker_api = config.get('APIs', 'broker_api')

        # Data params
        self.historical_data_frequency = Period(config.get('APIs', 'historical_data_frequency', fallback='1d')) # can be 1min, 5min, 10min, 1d, 1w etc
        self.historical_data_horizon = Period(config.get('APIs', 'historical_data_horizon', fallback='1M'))
        self.intraday_interval = Period(config.get('APIs', 'intraday_interval', fallback='5min'))

        # API keys
        load_dotenv()

        
    def _configure_log(self, log_level: str):
        if log_level == "Debug":
            return logging.DEBUG
        elif log_level == "Info":
            return logging.INFO
        elif log_level == "Warning":
            return logging.WARNING
        elif log_level == "Error":
            return logging.ERROR
        else:
            raise ValueError("Log level not recognized")
        
    def _configure_order_type(self, order_type: str) -> OrderType:
        if order_type.lower() == "market":
            return OrderType.MARKET
        elif order_type.lower() == "limit":
            raise NotImplementedError("")
            # return OrderType.LIMIT
        else:
            raise ValueError("Order type not recognized")
        
    def _check_limit_bounds(self):
        if self.limit_order_factor:
            if self.limit_order_factor < 0 or self.limit_order_factor > 1:
                raise ValueError("Limit price must be between 0 and 1")
        
