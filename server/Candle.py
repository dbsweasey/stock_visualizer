from collections import deque

class Candle:
    def __init__(self, time, price):
        self.time = time
        self.open = self.high = self.low = self.close = price

    def update(self, price):
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price

class TimeframeAggregator:
    def __init__(self, interval: int, history_size=1000):
        self.interval = interval

        self.current = None

        self.history = deque(maxlen=history_size)

    def process_tick(self, tick):
        timestamp = tick["timestamp"]
        price = tick["price"]

        bucket = (timestamp // self.interval) * self.interval

        if self.current is None:
            self.current = Candle(bucket, tick["price"])

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
    
class CandleEngine:
    def __init__(self):

        # Available intervals
        self.aggregators = {
            1: TimeframeAggregator(1),
            5: TimeframeAggregator(5),
            60: TimeframeAggregator(60)
        }

    def process_tick(self, tick):
        events = []

        for tf, agg in self.aggregators.items():

            candle = agg.process_tick(tick)
            if candle:
                events.append({
                    "type": "candle_closed",
                    "timeframe": tf,
                    "candle": candle
                })

            events.append({
                "type": "candle_update",
                "timeframe": tf,
                "candle": agg.current
            })
        return events
    
    def get_history(self, timeframe):
        agg = self.aggregators[timeframe]

        candles = list(agg.history)

        if agg.current:
            candles.append(agg.current)
        
        return candles