import time
import asyncio
import logging
logger = logging.getLogger(__name__)

from services.ingest import TICK_QUEUE

async def candle_consumer(engine, manager):
    """ Consumes a tick from TICK_QUEUE

    Reads the tick from queue when available. Passes it to the engine
    to develop a series of events.

    Args:
        engine (CandleEngine): The candle engine 
    """
    while True:
        tick = await TICK_QUEUE.get()

        events = engine.process_tick(tick)

        for event in events:
            await manager.broadcast(
                event
            )

async def candle_heartbeat(engine, manager):
    """ The heartbeat of the architecture. Ensures candles are closed at the 
    end of every interval, providing a continuous stream of data regardless of
    the volatility of market data.

    Checks whether a candle should be closed based on the current time. If so,
    broadcasts all close events. 

    Fires often to ensure no candle is closed too late. 

    Args:
        engine (CandleEngine): The engine responsible for the internal clock and handling candles,
            provides .check_heartbeat()

        manager (ConnectionManager): The WebSocket manager, provides .broadcast()
    """
    while True:
        try:
            now = time.time()
            # Gets list of candle_closed events
            events = engine.check_heartbeat(now)

            # Broadcast to the client
            for event in events:
                await manager.broadcast(event)
                
        except asyncio.CancelledError:
            logger.info("Candle heartbeat shutting down gracefully")
            raise
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        await asyncio.sleep(0.05)