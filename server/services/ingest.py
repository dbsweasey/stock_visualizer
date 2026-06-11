import asyncio
import random
import time

from alpaca.data.live import StockDataStream

from models.tick import Tick
from config import AVAILABLE_SYMBOLS, ALPACA_API_KEY, ALPACA_SECRET

import logging
logger = logging.getLogger(__name__)

TICK_QUEUE = asyncio.Queue()

stock_stream = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET)

async def random_ingest():
    price = 100.0
    price_map = {symbol: 100.0 for symbol in AVAILABLE_SYMBOLS}

    while True:
        for symbol in price_map:
            change = random.uniform(-0.5, 0.5)
            price = price_map[symbol] * (1 + change / 100)
            price = round(price, 2)
            price_map[symbol] = price
            tick = Tick(price, symbol, time.time())
            await TICK_QUEUE.put(tick)
            logger.info(f"Ingesting tick from {symbol}...")

        await asyncio.sleep(1)

async def data_ingest(data):
    logger.info("Callback.")
    logger.info(data)

async def ingest():
    stock_stream.subscribe_trades(data_ingest, "SPY", "AAPL", "TSLA", "NVDA", "MSFT")
    
    try:
        await stock_stream._run_forever()
    finally:
        await stock_stream.stop()

# Not working, legacy code.
'''
dotenv.load_dotenv()

FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")
FINNHUB_WS = f"wss://ws.finnhub.io?token={FINNHUB_TOKEN}"
SYMBOL = "NVDA"


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
'''