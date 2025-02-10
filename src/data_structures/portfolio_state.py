from src.data_structures.position import Position 
import logging
from src.readers.abstract_apis import AbstractBrokerAPI


class PortfolioState:
    """Class to track the state of our portfolio"""

    def __init__(self):
        self._portfolio: dict[str, Position] = {}
        self._cash: float = 0.0
        self._equity: float = 0.0

    @property
    def portfolio(self) -> dict[str, Position]:
        return self._portfolio
    
    @portfolio.setter
    def portfolio(self, other_positions: dict[str, Position]) -> None:
        self._portfolio = other_positions

    @property
    def cash(self) -> float:
        return self._cash
    
    @cash.setter
    def cash(self, cash: float) -> None:
        self._cash = cash

    @property
    def equity(self) -> float:
        return self._equity
    
    @equity.setter
    def equity(self, equity: float) -> None:
        self._equity = equity

    def __getitem__(self, ticker: str) -> Position:
        return self._portfolio[ticker]

    def __setitem__(self, ticker: str, value) -> None:
        self._portfolio[ticker] = value

    def __delitem__(self, ticker: str) -> None:
        del self._portfolio[ticker]

    def populate_state(self, broker_api: AbstractBrokerAPI) -> None:
        logging.info(f"Populating portfolio state")
        self.portfolio = {position.ticker: position for position in broker_api.get_all_positions()}
        self.cash = broker_api.get_cash()
        self.equity = broker_api.get_equity()

    def exists(self, ticker: str) -> bool:
        return True if ticker in self.portfolio else False
    
    def __repr__(self):
        return f"PortfolioState: {self.portfolio}, Cash: {self.cash}, Equity: {self.equity}"
    

        