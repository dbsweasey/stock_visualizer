from dataclasses import dataclass

@dataclass
class Candle:
    """ Defines a candle for the backend using the typical OHLC model.
    The time should be an bucketed integer for proper handling. 

    Open, high, low, and close prices are handled internally. Calling
    .update() will automatically adjust these fields.

    The constructor requires the following args:
    Args:
        time (int): the open time of the candle
        price (float): initial candle price
    """
    time: int
    open: float
    high: float
    low: float
    close: float

    def __init__(self, time, price):
        self.time = time
        self.open = self.high = self.low = self.close = price

    def update(self, price):
        """ Updates an existing candle with a new price

        Automatically adjusts high, low, and close.

        Args:
            price (float): New price of the candle
        """
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price