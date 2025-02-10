from src.execution.workflow import Task
from src.execution.context import Context
import logging
from src.strategys.market_open_momentum_strategy import MarketOpenMomentumStrategy
from src.strategys.sentiment_strategy import BERTBasedSentimentStrategy
from src.utilities.risk_manager import RiskManager
from src.utilities.statistics_gatherer import StatisticsGatherer
from src.utilities.enums import Signal, OrderType
from src.data_structures.order import Order
from src.data_structures.portfolio_state import PortfolioState
from src.readers.api_factories import BrokerAPIFactory, MarketDataAPIFactory
from src.data_structures.marketdata_state import MarketDataState
from src.services.market_data_service import MarketDataService
from src.utilities.utils import market_open
import sys
from src.execution.configuration import Configuration



class GenericBotApplication(Task):

    def execute(self, cfg: Configuration):
        logging.info("Running GenericBotApp")

        mkdata_factory = MarketDataAPIFactory()
        mkdata_api = mkdata_factory.create_instance(cfg.market_data_api)

        broker_api = BrokerAPIFactory.create_instance(cfg.broker_api)
        broker_api.connect(cfg)
        
        portfolio_state = PortfolioState()
        portfolio_state.populate_state(broker_api)

        mkdata_state = MarketDataState()
        mkdata_state.add_apis({cfg.market_data_api: mkdata_api})
        mkdata_state.populate_historical_data(cfg.tickers, cfg)
        mkdata_state.populate_intraday_data(cfg.tickers, cfg)

        mkdata_service = MarketDataService(mkdata_state)

        risk_manager = RiskManager(cfg.position_sizing, cfg.stop_loss, cfg.take_profit, cfg.max_exposure, portfolio_state)
        statistics_gatherer = StatisticsGatherer()

        while market_open(cfg.market):
        
            stop_loss_trades = risk_manager.check_stop_loss()
            broker_api.close_positions(stop_loss_trades)
            statistics_gatherer.increment_stop_loss(stop_loss_trades)

            take_profit_tickers = risk_manager.check_take_profit()
            broker_api.close_positions(take_profit_tickers)
            statistics_gatherer.increment_take_profit(take_profit_tickers)

            # signals = MarketOpenMomentumStrategy.generate_signals(mkdata_service, cfg.tickers, cfg)
            signals = BERTBasedSentimentStrategy.generate_signals(mkdata_service, cfg.tickers, cfg)
            
            orders = []
            prices = {}
            for ticker, signal in signals.items():
                price = mkdata_service.get_real_time_price(ticker)
                units = risk_manager.units_to_trade(price)

                orders.append(Order(ticker, signal, units, None, cfg.order_type))
                prices[ticker] = price

            approved_orders = risk_manager.check_max_exposures(orders, prices)
            broker_api.place_orders(approved_orders)

            statistics_gatherer.increment_signals(signals)
            logging.info(f"Current cumulative signals: \n{str(statistics_gatherer.to_dataframe())}")

            portfolio_state.populate_state(broker_api)
            mkdata_state.populate_state(cfg)








        