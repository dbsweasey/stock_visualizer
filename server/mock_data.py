import asyncio
import random
import time

from ConnectionManager import ConnectionManager
from Candle import Candle

TICK_QUEUE = asyncio.Queue()

async def random_ingest():
    price = 100.0
    count = 0

    while True:
        change = random.uniform(-0.5, 0.5)
        price *= 1 + change / 100
        price = round(price, 2)
        count += 1 

        tick = {"price": price, "timestamp": time.time()}

        await TICK_QUEUE.put(tick)
        print(f'This is tick #{count} since server boot')
        await asyncio.sleep(1)

async def candle_consumer(engine, manager):
    while True:
        tick = await TICK_QUEUE.get()

        events = engine.process_tick(tick)

        for event in events:
            await manager.broadcast(
                event["timeframe"],
                event
            )