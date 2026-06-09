from engine.timeframe_aggregator import TimeframeAggregator
from models.event import Event

from config import AVAILABLE_INTERVALS

class CandleEngine:
    def __init__(self):

        # Available intervals
        self.aggregators = {
            interval: TimeframeAggregator(interval)
            for interval in AVAILABLE_INTERVALS
        }

    def process_tick(self, tick):
        events = []

        for tf, agg in self.aggregators.items():

            candle = agg.process_tick(tick)
            if candle:
                events.append(Event("candle_closed", tf, candle))

            events.append(Event("candle_update", tf, agg.current))
        return events
    
    def get_history(self, timeframe):
        agg = self.aggregators[timeframe]

        candles = list(agg.history)

        if agg.current:
            candles.append(agg.current)
        
        return candles