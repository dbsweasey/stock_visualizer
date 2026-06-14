import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from websocket.connection_manager import ConnectionManager
from websocket.handlers import WebSocketHandler
from engine.candle_engine import CandleEngine

from services.ingest import ingest, random_ingest_basic, random_ingest_high_frequency
from services.candle_consumer import candle_consumer, candle_heartbeat

from config import AVAILABLE_INTERVALS_MAP, AVAILABLE_SYMBOLS, PORT, ADDRESS

from utils.logging import setup_logging

setup_logging()

# Establish three important components
manager = ConnectionManager()
engine = CandleEngine()
ws_handler = WebSocketHandler(manager, engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Producer ingests ticks
    producer = asyncio.create_task(random_ingest_basic(delay_low=0.5, delay_high=0.5, change_high=3, change_low=-3))
    # Consumer takes ticks and updates candles
    consumer = asyncio.create_task(candle_consumer(engine, manager))
    # Ensures candles are closed at a fixed rate (based on interval)
    heartbeat = asyncio.create_task(candle_heartbeat(engine, manager))

    try:
        yield
    finally:
        producer.cancel()
        consumer.cancel()
        heartbeat.cancel()
        await asyncio.gather(producer, consumer, heartbeat, return_exceptions=True)

# Start app
app = FastAPI(lifespan=lifespan)

# Restrict who can directly access backend (must be an authorized client)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{PORT}",
        f"http://{ADDRESS}:{PORT}"
    ]
)

# GET intervals and symbols, sent to client. Backend ultimate source of truth
@app.get("/config")
def config():
    return {"intervals": AVAILABLE_INTERVALS_MAP, "symbols": AVAILABLE_SYMBOLS}

# Establish connection
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws_handler.handle_connection(ws)

