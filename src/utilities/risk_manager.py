from src.data_structures.order import Order
from src.data_structures.position import Position
from src.data_structures.portfolio_state import PortfolioState
import logging
from src.utilities.statistics_gatherer import StatisticsGatherer


class RiskManager:
    """
    Provides methods for validating orders and tracking positions.
    """

    def __init__(self, 
                 position_sizing: float, 
                 stop_loss_factor: float, 
                 take_profit_factor: float,
                 max_exposure: float,
                 ptf_state: PortfolioState
                 ) -> None:
        self.position_sizing = position_sizing
        self.stop_loss_factor = stop_loss_factor
        self.take_profit_factor = take_profit_factor
        self.max_exposure = max_exposure
        self.state = ptf_state

    def check_max_exposures(self, orders: list[Order], prices: dict[str, float]) -> dict[str, bool]:
        """
        Validate an order against risk management rules.

        :param order: The order to validate.
        :param latest_price: The latest price of the asset.
        :return: True if the order is valid, otherwise False.

        Notes
        -----
        An order is valid iff:
        1. The asset is not already in the portfolio.
        2. The order combined with the existing exposure does not exceed the maximum exposure.
        """
        approved_orders = []
        for order in orders:
            order_market_value = order.quantity * prices[order.ticker]

            if not self.state.exists(order.ticker) and order_market_value / self.state.equity < self.max_exposure:
                logging.debug(f"Risk Mgr: Ticker {order.ticker} not in PTF and exposure below max. Can perform trade.")
                approved_orders.append(order)
            
            elif (self.state[order.ticker].market_value + order_market_value) / self.state.equity < self.max_exposure:
                exposure = (self.state[order.ticker].market_value + order_market_value) / self.state.equity
                logging.debug(f"Risk Mgr: Exposure to {order.ticker} will be {exposure} < {self.max_exposure}.")
                logging.debug("Risk Mgr: Can perform trade.")
                approved_orders.append(order)
        
        return approved_orders
        
    def check_stop_loss(self) -> list[str]:
        """
        Apply the stop loss rule to a position.

        :param ticker: The ticker of the asset.
        :return: True if the stop loss must be applied, otherwise False.
        """
        stop_losses = []
        for ticker in self.state.portfolio.keys():
            if self.state.exists(ticker):
                position = self.state[ticker]
                stop_loss_price = (1 - self.stop_loss_factor) * position.average_purchase_price * position.quantity
                logging.debug(f"Risk Mgr: {ticker} market value: {position.market_value}. Stop loss level: {stop_loss_price}.")

                if position.market_value < stop_loss_price:
                    stop_losses.append(ticker)
        
        return stop_losses
        
    def check_take_profit(self) -> list[str]:
        """
        Apply the take profit rule to a position.

        :param ticker: The ticker of the asset.
        :return: True if we take the profit, otherwise False.
        """
        take_profits = []
        for ticker in self.state.portfolio.keys():
            if self.state.exists(ticker):
                position = self.state[ticker]
                take_profit_level = (1 + self.take_profit_factor) * position.average_purchase_price * position.quantity
                logging.debug(f"Risk Mgr: {ticker} market value: {position.market_value}. Take profit level: {take_profit_level}.")

                if position.market_value >= take_profit_level:
                    take_profits.append(ticker)
        
        return take_profits
        
    def units_to_trade(self, price: float) -> float:
        """
        Calculate the number of units to trade based on available cash.

        :param price: The current price of the asset.
        :return: The number of units to trade.
        """
        logging.debug(f"Risk Mgr: Calculating units to trade")
        return self.position_sizing / price
