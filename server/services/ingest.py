import asyncio
import random
import time

from alpaca.data.live import StockDataStream

from models.tick import Tick
from config import AVAILABLE_SYMBOLS, ALPACA_API_KEY, ALPACA_SECRET

import logging
logger = logging.getLogger(__name__)

# Establish the queue for incoming ticks
TICK_QUEUE = asyncio.Queue()

# Build the Alpaca stream
stock_stream = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET)

# A random, simple tick generator
async def random_ingest_basic(delay_low: float=0.5, delay_high: float=4.0, change_low: float=-0.5, change_high=0.5):
    """ Randomly generates one tick per symbol every random interval

    Extremely basic ingestion task, ensures websocket communication channel is 
    established to the frontend.

    Args:
        delay_low (float): shortest possible random tick delay

        delay_high (float): highest possible random tick delay

        change_low (float): lowest possible random change%

        change_high (float): highest possible random change%
    """
    # Init all symbols at $100
    price_map = {symbol: 100.0 for symbol in AVAILABLE_SYMBOLS}

    while True:
        for symbol in price_map:
            # 1. Generate %change
            change = random.uniform(change_low, change_high)

            # 2. Update and round price
            price = price_map[symbol] * (1 + change / 100)
            price = round(price, 2)
            price_map[symbol] = price

            # 3. Create tick, add to queue
            tick = Tick(price, symbol, time.time())
            await TICK_QUEUE.put(tick)
        
        # 4. Wait for random time
        # logger.info("---TICK---")
        await asyncio.sleep(random.uniform(delay_low, delay_high))

# High freq digestion function
async def random_ingest_high_frequency(tps: int = 500, stall: bool = True):
    """ High frequency ingesting function that closely resembles real market data.

    Generates random base prices and price change, includes network jitter, 
    and includes random dead market lulls.

    Args:
        tps (int): Ticks per second
        stall (bool): Include market lulls

    Raises:
        Exception: catch all for async issue
        CancelledError: allows graceful handling of job cancellation 
    """
    logger.info(f"Starting aftermarket load test at {tps} TPS...")
    
    # Give baseline starting prices to symbols
    prices = {symbol: random.uniform(50.0, 500.0) for symbol in AVAILABLE_SYMBOLS}
    base_sleep = 1.0 / tps

    while True:
        try:
            # 1. Simulate intermittent dead zones to test Synthetic Candles
            if stall and random.random() < 0.02: # 2% chance to stall
                pause_time = random.uniform(2.0, 6.0)
                logger.info(f"--- SIMULATING MARKET LULL FOR {pause_time:.1f}s ---")
                await asyncio.sleep(pause_time)

            # Pick a random symbol
            symbol = random.choice(AVAILABLE_SYMBOLS)
            
            # Generate random new price
            prices[symbol] += random.uniform(-0.10, 0.10)
            price = round(prices[symbol], 2)
            
            # 2. Simulate timestamp
            exchange_time_secs = time.time()
            
            # Simulate slight network jitter (ticks arriving up to 200ms late)
            if random.random() < 0.1:
                exchange_time_secs -= random.uniform(0.05, 0.20)
                
            # Create tick, add to queue
            tick = Tick(
                price, symbol, exchange_time_secs 
            )
            
            await TICK_QUEUE.put(tick)

            # Sleep (based on tps)
            await asyncio.sleep(base_sleep)
            
        except asyncio.CancelledError:
            logger.info("Load test ingestion stopped gracefully.")
            raise
        except Exception as e:
            logger.error(f"Error in mock ingest: {e}")
            await asyncio.sleep(1)


async def get_market_data(data):
    """ Callback function for stock_stream, adds tick to queue to be digested.
        This is the "producer" in the producer/consumer model.
    """
    tick = Tick(data.price, data.symbol, data.timestamp.timestamp())
    await TICK_QUEUE.put(tick)


async def ingest():
    """ Subscribes to live market trades forever. Yields control when no incoming
        data.
    """
    stock_stream.subscribe_trades(get_market_data, *AVAILABLE_SYMBOLS)
    
    try:
        await stock_stream._run_forever()
    finally:
        await stock_stream.stop()
