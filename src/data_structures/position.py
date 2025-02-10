

class Position:
    """
    Tracks an open position in a financial instrument.

    Maintains details like quantity, average price, and unrealized PnL.
    """

    def __init__(self, 
                 ticker: str, 
                 direction: str, 
                 quantity: float, 
                 average_purchase_price: float,
                 exchange: str = None,
                 market_value: float = None,
                 current_price: float = None,
                 unrealized_pnl: float = None
                 ) -> None:
        self.ticker = ticker
        self.direction = direction
        self.quantity = quantity
        self.average_purchase_price = average_purchase_price
        self.exchange = exchange
        self.market_value = market_value
        self.current_price = current_price
        self.unrealized_pnl = unrealized_pnl
