import asyncio

import logging
logger = logging.getLogger(__name__)

from engine.timeframe_aggregator import TimeframeAggregator
from models.event import Event
from models.tick import Tick
from utils.time import get_next_boundry, current, get_bucket

from config import AVAILABLE_INTERVALS, AVAILABLE_SYMBOLS

class CandleEngine:
    """ Handles tick to candle pipeline, the internal clock, and holds
        aggregators (symbol, interval)

        This is the heart of the architecture. Need one to run the system

        The constructor registers all symbols and intervals. These are defined in config.py

        Args:
            grace_period (float): Time, in seconds, to allow a lagging tick to enter a candle before it closes
    """
    def __init__(self, grace_period: float = 0.3):
        self.grace_period = grace_period

        # Available intervals
        self.aggregators = {}
        for symbol in AVAILABLE_SYMBOLS:
            self.register_symbol(symbol)
    
    def register_symbol(self, symbol: str):
        """ Creates aggregators for all intervals for the provided symbol.

        Args:
            symbol (str): The stock ticker symbol to register 
        """
        
        # If symbol is already registered, skip
        if symbol in self.aggregators:
            return

        logger.info(f"Registering {symbol} to CandleEngine")
        
        # Create aggs for all intervals. 
        self.aggregators[symbol] = {
            interval: TimeframeAggregator(interval)
            for interval in AVAILABLE_INTERVALS
        }

    def process_tick(self, tick: Tick):
        """ Given a tick object, process it, and return a list of events

        These events will be broadcast to the frontend. Takes
        the tick price and timestamp, appropriately buckets the new price into an existing candle,
        and returns a descriptive candle_update event. Calls upon each aggregator for 
        the symbol to do the bulk of the processing. 

        Args: 
            tick (Tick): A tick object to process. 
        
        Raises:
            ValueError: if a Tick's symbol is not initialized
        """
        
        symbol = tick.symbol

        # Check if symbol is registered
        if symbol not in self.aggregators:
            raise ValueError(f"{symbol} not initialized")
        
        events = []
        for tf, agg in self.aggregators[symbol].items():
            # Update the candle based on tick
            agg.process_tick(tick)
            
            # Create an event for the updated candle
            if agg.current:
                events.append(Event("candle_update", symbol, tf, agg.current))
            
        return events
    
    def get_history(self, symbol: str, interval: int):
        """ Retrieves the candle series history stored within an aggregator

        Based on the symbol and interval, check the aggregator and retrieve
        the candle series history from it. Returns all historic candles plus
        the current to be sent to the frontend.

        Args:
            symbol (str): The stock ticker symbol
            interval(int): The interval, in seconds 
        """
        agg = self.aggregators[symbol][interval]

        candles = list(agg.history)

        # Adding currently building candle
        if agg.current:
            candles.append(agg.current)
        
        return candles
    
    def check_heartbeat(self, timestamp: int):
        """Checks whether the heartbeat time has elapsed and a candle should be closed
        
        Iterates through all aggregators. If the timestamp passes the bucket close time,
        creates a candle_close event.
        
        Args:
            timestamp (int): the current system time (in seconds)
        """
        events = []
        for symbol, intervals in self.aggregators.items():
            for tf, agg in intervals.items():
                if not agg.current:
                    continue

                candle_end_time = agg.current.time + tf
                
                # If time is passed the end (allowing for grace period)
                if timestamp >= (candle_end_time + self.grace_period):
                    next_bucket_time = candle_end_time
                    
                    # Call advance candle, which creates new candle and closes this one
                    closed_candle = agg.advance_candle(next_bucket_time)

                    if closed_candle:
                        events.append(Event("candle_closed", symbol, tf, closed_candle))
                        events.append(Event("candle_update", symbol, tf, agg.current))
        return events
