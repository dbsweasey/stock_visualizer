from services.ingest import TICK_QUEUE

async def candle_consumer(engine, manager):
    while True:
        tick = await TICK_QUEUE.get()

        events = engine.process_tick(tick)

        for event in events:
            await manager.broadcast(
                event.timeframe,
                event.__dict__
            )