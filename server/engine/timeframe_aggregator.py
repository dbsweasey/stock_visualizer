from collections import deque

from models.candle import Candle

from utils.time import get_bucket

class TimeframeAggregator:
    def __init__(self, interval: int, history_size=1000):
        self.interval = interval

        self.current = None

        self.history = deque(maxlen=history_size)

    def process_tick(self, tick):
        price = tick.price

        bucket = get_bucket(tick.timestamp, self.interval)

        if self.current is None:
            self.current = Candle(bucket, price)

            return None
        
        if bucket != self.current.time:
            self.current.update(price)
            self.history.append(self.current)

            closed = self.current

            self.current = Candle(bucket, self.current.close)
            self.current.update(price)

            return closed

        self.current.update(price)

        return None