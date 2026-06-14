from collections import deque

import logging
logger = logging.getLogger(__name__)

from models.candle import Candle

from utils.time import get_bucket
class TimeframeAggregator:
    """ Handles candle production for a specific interval. Stores candles
    for retrieval if the frontend changes views. 

    Args:
        interval (int): The interval of the candles (1s, 5s, etc.)
        history_size (int): How long the candle history should be
    
    """
    def __init__(self, interval: int, history_size=1000):
        self.interval = interval

        self.current = None

        self.history = deque(maxlen=history_size)

    def process_tick(self, tick):
        """ Given a tick, updates the price of the current candle.
        If there is no current candle, creates one. The graph starts upon the first tick.
        """
        price = tick.price

        bucket = get_bucket(tick.timestamp, self.interval)

        if self.current is None:
            self.current = Candle(bucket, price)

            return
        
        if bucket == self.current.time:
            self.current.update(price)

    def advance_candle(self, next_bucket_time: int):
        """ Create a new candle, close the old candle
        
        Args:
            next_bucket_time (int): the start of the next candle
        """
        if self.current is None:
            return None

        closed_candle = self.current
        self.history.append(closed_candle)

        self.current = Candle(next_bucket_time, closed_candle.close)

        return closed_candle                                                                                                                                                                                                                                                                    
