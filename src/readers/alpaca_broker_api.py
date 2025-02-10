from src.readers.abstract_apis import AbstractBrokerAPI
import logging
from src.execution.configuration import Configuration
from src.data_structures.order import Order
from src.data_structures.position import Position
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from src.utilities.enums import Signal, PositionDirection, Exchange
import os


class AlpacaAPI(AbstractBrokerAPI):
    __slots__ = ("client_api")

    def __init__(self) -> None:
        """
        Initialize AlpacaAPI instance without an active connection.
        """
        super().__init__()
        self.client_api = None

    def connect(self, config: Configuration) -> None:
        """
        Connect to the Alpaca API using the provided configuration.

        :param config: Configuration object containing API keys and settings.
        """
        try:
            self.client_api = TradingClient(
                api_key=os.environ.get('ALPACA_KEY', 'WRONG-KEY'),
                secret_key=os.environ.get('ALPACA_SECRET', 'WRONG-KEY'),
                paper=config.paper_trading,
            )
            logging.info("Successfully connected to Alpaca client.")
        except Exception as err:
            logging.error(f"Failed to connect to Alpaca API: {err}")
            raise

    def account_details(self):
        return self.client_api.get_account()

    def place_market_order(self, order: Order) -> None:
        """
        Place a market order.

        :param order: The order object containing trade details.
        :param state: The portfolio state to update upon successful order placement.
        """
        if order.direction == Signal.BUY:
            side = OrderSide.BUY
        elif order.direction == Signal.SELL:
            side = OrderSide.SELL
        elif order.direction == Signal.HOLD:
            logging.debug(f"Order direction is HOLD, no order placed")
            return None
        else:
            raise ValueError(f"Invalid order direction: {order.direction}")
        
        try:
            market_order_data = MarketOrderRequest(symbol=order.ticker, qty=order.quantity, side=side, time_in_force=TimeInForce.DAY)
            self.client_api.submit_order(order_data=market_order_data)
            logging.debug(f"Market order successfully submitted")

        except Exception as err:
            logging.error(f"Error placing market order: {order}. Error: {err}")

    def place_limit_order(self, order: Order) -> None:
        """
        Place a limit order.

        :param order: The order object containing trade details.
        :param state: The portfolio state to update upon successful order placement.
        """
        if order.direction == Signal.BUY:
            side = OrderSide.BUY
        elif order.direction == Signal.SELL:
            side = OrderSide.SELL
        elif order.direction == Signal.HOLD:
            logging.debug(f"Order direction is HOLD, no order placed")
            return None
        else:
            raise ValueError(f"Invalid order direction: {order.direction}")
            
        try:
            limit_order = LimitOrderRequest(
                symbol=order.ticker,
                qty=order.quantity,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=order.price,
            )
            self.client_api.submit_order(order_data=limit_order)
            logging.debug(f"Limit order placed successfully")

        except Exception as err:
            logging.error(f"Error placing limit order: {order}. Error: {err}")

    def get_all_positions(self) -> list[Position]:
        """
        Retrieve all open positions from the Alpaca account.

        :return: A list of Position objects representing current holdings.
        """
        try:
            raw_positions = self.client_api.get_all_positions()
            return [self.__parse_position(position) for position in raw_positions]

        except Exception as err:
            logging.error(f"Error retrieving all positions: {err}")
            raise

    def get_cash(self) -> float:
        """
        Retrieve the available cash balance in the trading account.

        :return: The available cash as a float.
        """
        try:
            return float(self.client_api.get_account().cash)
        except Exception as err:
            logging.error(f"Error retrieving cash in account: {err}")

    def get_equity(self) -> float:
        """
        Retrieve the total equity balance in the trading account.

        :return: The equity amount as a float.
        """
        try:
            return float(self.client_api.get_account().equity)
        except Exception as err:
            logging.error(f"Error retrieving cash in account: {err}")

    def close_all_positions(self) -> list[Position]:
        """
        Close all open positions in the Alpaca account.

        :return: A list of Position objects representing closed positions.
        """
        try:
            self.client_api.close_all_positions(cancel_orders=True) 
            logging.info("All positions successfully closed.")
        except Exception as err:
            logging.error(f"Error closing all positions: {err}")
            raise

    def close_positions(self, tickers: list[str]) -> None:
        for ticker in tickers:
            try:
                self.client_api.close_position(symbol_or_asset_id=ticker) 
                logging.debug("Posiotion {} successfully closed")
            except Exception as err:
                logging.error(f"Error closing position: {err}")
                raise

    def __parse_position(self, position) -> Position:
        """
        Parse a raw position dictionary into a Position object.

        :param position: A dictionary containing raw position data.
        :return: A Position object representing the raw data.
        """
        exchange = None

        if position.exchange == "NASDAQ":
            exchange = Exchange.NASDAQ
        elif position.exchange == "NYSE":
            exchange = Exchange.NYSE
        elif position.exchange == "CRYPTO":
            exchange = Exchange.CRYPTO
        elif position.exchange == "":
            exchange = Exchange.EMPTY
        else:
            exchange = Exchange.UNKNOWN

        return Position(
            position.symbol,
            PositionDirection.LONG if position.side == "long" else PositionDirection.SHORT,
            float(position.qty),
            float(position.avg_entry_price),
            exchange,
            float(position.market_value),
            float(position.current_price),
            float(position.unrealized_pl)
            )




