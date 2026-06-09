import asyncio

from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

from websocket.connection_manager import ConnectionManager
from websocket.handlers import WebSocketHandler
from engine.candle_engine import CandleEngine

from services.ingest import random_ingest
from services.candle_consumer import candle_consumer

from utils.logging import setup_logging

setup_logging()

manager = ConnectionManager()
engine = CandleEngine()
ws_handler = WebSocketHandler(manager, engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = asyncio.create_task(random_ingest())
    consumer = asyncio.create_task(candle_consumer(engine, manager))

    try:
        yield
    finally:
        producer.cancel()
        consumer.cancel()
        await asyncio.gather(producer, consumer, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws_handler.handle_connection(ws)

