from src.strategys.abstract_strategy import AbstractStrategy
import logging
from src.utilities.enums import Signal
from src.services.market_data_service import MarketDataService
from src.execution.configuration import Configuration
import pandas as pd
from src.utilities.utils import timezone_from_calendar


class MarketOpenMomentumStrategy(AbstractStrategy):

    @staticmethod
    def generate_signals(mkdata_service: MarketDataService, tickers: list[str], cfg: Configuration) -> dict[str, Signal]:        
        logging.info(f"Generating signals using {__class__.__name__}")
        signals = {}

        now = pd.Timestamp.now(tz=timezone_from_calendar(cfg.market))
        today = now.normalize()

        for ticker in tickers:
            current_price = mkdata_service.get_real_time_price(ticker, cfg.market_data_api)
            open_price = mkdata_service.get_price(cfg.market_data_api, ticker, today, 'open')

            message_str = f"{ticker} open price: {open_price}.  Current price: {current_price}"
            logging.debug(message_str)

            if open_price < current_price:
                signal = Signal.BUY
            elif open_price > current_price:
                signal = Signal.SELL
            else:
                signal = Signal.HOLD

            signals[ticker] = signal

            logging.info(f"Signal for {ticker}: {signal}")
            return signals
    