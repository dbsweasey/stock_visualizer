import asyncio
import random
import time

from models.tick import Tick

import logging
logger = logging.getLogger(__name__)

TICK_QUEUE = asyncio.Queue()

async def random_ingest():
    price = 100.0
    count = 0

    while True:
        change = random.uniform(-0.5, 0.5)
        price *= 1 + change / 100
        price = round(price, 2)
        count += 1 

        tick = Tick(price, time.time())

        await TICK_QUEUE.put(tick)
        logger.info(f"Creating tick #{count} since server boot")
        await asyncio.sleep(1)

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