import logging
logger = logging.getLogger(__name__)

from engine.timeframe_aggregator import TimeframeAggregator
from models.event import Event
from models.tick import Tick

from config import AVAILABLE_INTERVALS
from config import AVAILABLE_SYMBOLS

class CandleEngine:
    def __init__(self):

        # Available intervals
        self.aggregators = {}
        for symbol in AVAILABLE_SYMBOLS:
            self.register_symbol(symbol)
    
    def register_symbol(self, symbol: str):
        if symbol in self.aggregators:
            return
        logger.info(f"Registering {symbol} to CandleEngine")
        self.aggregators[symbol] = {
            interval: TimeframeAggregator(interval)
            for interval in AVAILABLE_INTERVALS
        }

    def process_tick(self, tick: Tick):
        symbol = tick.symbol
        logger.info(f"Processing {symbol} tick (price: {tick.price}, time: {tick.timestamp})")
        if symbol not in self.aggregators:
            raise ValueError(f"{symbol} not initialized")
        events = []
        for tf, agg in self.aggregators[symbol].items():
            candle = agg.process_tick(tick)
            if candle:
                events.append(Event("candle_closed", symbol, tf, candle))

            events.append(Event("candle_update", symbol, tf, agg.current))
        return events
    
    def get_history(self, symbol: str, interval: int):
        agg = self.aggregators[symbol][interval]

        candles = list(agg.history)

        if agg.current:
            candles.append(agg.current)
        
        return candles