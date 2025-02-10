

class Order:
    """
    Represents a trade order.

    Encapsulates details like ticker, quantity, price, and side (buy/sell).
    """

    def __init__(self, ticker: str, direction: str, quantity: float, price: float | None, type: str) -> None:
        self.ticker = ticker
        self.direction = direction 
        self.quantity = quantity
        self.price = price
        self.type = type

    def __str__(self):
        class_str =  f"Order(ticker={self.ticker}, direction={self.direction}, "
        class_str += f"quantity={self.quantity}, price={self.price}, type={self.type})"
        return class_str

