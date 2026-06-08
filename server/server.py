import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

from ConnectionManager import ConnectionManager
from Candle import CandleEngine

import mock_data

manager = ConnectionManager()
engine = CandleEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    ingest = asyncio.create_task(mock_data.random_ingest())
    aggregate = asyncio.create_task(mock_data.candle_consumer(engine, manager))

    try:
        yield
    finally:
        ingest.cancel()
        aggregate.cancel()
        await asyncio.gather(ingest, aggregate, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)

    candles = list(engine.aggregators[5].history)
    await ws.send_json({
        "type": "snapshot",
        "candles": [c.__dict__ for c in candles]
    })

    try:
        while True:
            msg = await ws.receive_json()
            if msg["type"] == "update_interval":
                interval = msg["interval"]
                manager.subscribe(ws, interval)
                candles = engine.get_history(interval)
                await ws.send_json({
                    "type": "snapshot",
                    "candles": [c.__dict__ for c in candles]
                })
    
    except WebSocketDisconnect:
        manager.disconnect(ws)

