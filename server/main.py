import asyncio
import json
import websockets
from collections import deque
import random
import time

FINNHUB_TOKEN = "d5a4f7hr01qu56n04dd0d5a4f7hr01qu56n04ddg"
FINNHUB_WS = f"wss://ws.finnhub.io?token={FINNHUB_TOKEN}"
SYMBOL = "NVDA"

TICK_QUEUE = asyncio.Queue()


async def random_ingest():
    price = 100.0

    while True:
        change = random.uniform(-0.5, 0.5)
        price *= 1 + change / 100
        price = round(price, 2)

        tick = {"price": price, "timestamp": time.time()}

        await TICK_QUEUE.put(tick)
        await asyncio.sleep(1)


async def finnhub_ingest():
    while True:
        try:
            async with websockets.connect(FINNHUB_WS) as ws:
                await ws.send(json.dumps({"type": "subscribe", "symbol": SYMBOL}))

                async for msg in ws:
                    data = json.loads(msg)
                    print(data)
                    if "data" in data:
                        for tick in data["data"]:
                            await TICK_QUEUE.put(
                                {"price": tick["p"], "timestamp": tick["t"] / 1000}
                            )
        except Exception as e:
            print("Finnhub disconnected, retrying:", e)
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            print("Uh oh")
            break


class Candle:
    def __init__(self, time, price):
        self.time = time
        self.open = self.high = self.low = self.close = price

    def update(self, price):
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price


BASE_INTERVAL = 1.0
candles = deque(maxlen=300)
current = None
SUBSCRIBERS = set()


async def candle_aggregator():
    global current

    while True:
        try:
            tick = await TICK_QUEUE.get()
            ts = int(tick["timestamp"])
            bucket = (ts // BASE_INTERVAL) * BASE_INTERVAL

            if current is None:
                current = Candle(bucket, tick["price"])

            elif bucket != current.time:
                candles.append(current)

                await broadcast(
                    {
                        "type": "candle_closed",
                        "interval": BASE_INTERVAL,
                        "candle": current.__dict__,
                    }
                )

                current = Candle(bucket, current.close)
            current.update(tick["price"])

            await broadcast(
                {
                    "type": "candle_update",
                    "interval": BASE_INTERVAL,
                    "candle": current.__dict__,
                }
            )

        except asyncio.CancelledError:
            break


async def broadcast(message):
    for ws in list(SUBSCRIBERS):
        try:
            await ws.send_json(message)
        except:
            SUBSCRIBERS.remove(ws)


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    ingest_task = asyncio.create_task(random_ingest())
    aggregate_task = asyncio.create_task(candle_aggregator())

    try:
        yield
    finally:
        ingest_task.cancel()
        aggregate_task.cancel()
        await asyncio.gather(ingest_task, aggregate_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    await ws.send_json(
        {
            "type": "snapshot",
            "interval": BASE_INTERVAL,
            "candles": [c.__dict__ for c in candles],
        }
    )

    SUBSCRIBERS.add(ws)

    try:
        while True:
            try:
                msg = await ws.receive_json()
            except asyncio.TimeoutError:
                continue

            if msg["type"] == "update_interval":
                interval = int(msg["interval"])

                rebuilt = rebuild(candles, interval)
                await ws.send_json(
                    {"type": "chart", "interval": interval, "candles": rebuilt}
                )
    except WebSocketDisconnect:
        SUBSCRIBERS.remove(ws)


def rebuild(base_candles, interval):
    result = []
    current = None

    for c in base_candles:
        bucket = (c.time // interval) * interval

        if current is None or current["time"] != bucket:
            current = {
                "time": int(bucket),
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
            }
            result.append(current)
        else:
            current["high"] = max(current["high"], c.high)
            current["low"] = min(current["low"], c.low)
            current["close"] = c.close

    return result
