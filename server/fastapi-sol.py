import random
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import time


class Price:
    def __init__(self, price):
        self.price = price
        self.time = time.time()


app = FastAPI()

FAKE_OPEN = 1000
prices: list[Price] = []


# Will be replaced by Finnhub
def generate_fake_price(current_price):
    change = random.uniform(-2, 2)
    return round(current_price * (1 + change / 100), 2)


def bucket_time(ts, interval):
    return (ts // interval) * interval


def build_candles(prices, interval):
    candles = []
    if not prices or interval <= 0:
        return candles

    current_bucket = None
    o = h = l = c = None

    for p in prices:
        ts = int(p.time)
        b = bucket_time(ts, interval)
        if current_bucket is None:
            current_bucket = b
            h = l = c = p.price
            o = FAKE_OPEN
        elif b != current_bucket:
            candles.append(
                {"time": current_bucket, "open": o, "high": h, "low": l, "close": c}
            )
            current_bucket = b
            o = c
            c = h = l = p.price
        else:
            h = max(h, p.price)
            l = min(l, p.price)
            c = p.price

    if current_bucket is not None and o is not None:
        candles.append(
            {"time": current_bucket, "open": o, "high": h, "low": l, "close": c}
        )

    return candles


async def send_full_chart(interval, socket: WebSocket):
    candles = build_candles(prices, interval)
    await socket.send_json({"type": "chart", "candles": candles})
    return candles


@app.websocket("/ws/prices")
async def connect_socket(websocket: WebSocket):
    await websocket.accept()

    update_interval = 1

    current_bucket = None
    h = l = c = None
    o = FAKE_OPEN

    candles = await send_full_chart(update_interval, websocket)
    if candles:
        last = candles[-1]
        current_bucket = int(last["time"])
        o, h, l, c = last["open"], last["high"], last["low"], last["close"]

    async def send_stock_data():
        nonlocal o, h, l, c, current_bucket, update_interval
        price = FAKE_OPEN

        while True:
            price = generate_fake_price(price)
            tick = Price(price)
            prices.append(tick)

            ts = tick.time
            b = bucket_time(ts, update_interval)

            if current_bucket is None or b != current_bucket:
                current_bucket = b
                h = l = c = tick.price
                o = FAKE_OPEN if len(prices) <= 1 else prices[-2].price
            elif b != current_bucket:
                o = c
                h = l = c = o
            else:
                h = max(h, tick.price)
                l = min(l, tick.price)
                c = tick.price

            await websocket.send_json(
                {
                    "type": "ticker",
                    "symbol": "FAKE",
                    "tick": {
                        "time": current_bucket,
                        "opem": o,
                        "high": h,
                        "low": l,
                        "close": c,
                    },
                }
            )

            await asyncio.sleep(1)

    send_task = asyncio.create_task(send_stock_data())

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)

            if data.get("type") == "update_interval":
                update_interval = int(data["interval"])

                candles = await send_full_chart(update_interval, websocket)

                if candles:
                    last = candles[-1]
                    current_bucket = int(last["time"])
                    o, h, l, c = last["open"], last["high"], last["low"], last["close"]
                else:
                    current_bucket = None
    except WebSocketDisconnect:
        print("Client disconnected")
        send_task.cancel()
