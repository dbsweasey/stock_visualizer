from dataclasses import dataclass

@dataclass
class Candle:
    time: float
    open: float
    high: float
    low: float
    close: float

    def __init__(self, time, price):
        self.time = time
        self.open = self.high = self.low = self.close = price

    def update(self, price):
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price