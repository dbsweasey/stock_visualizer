from config import ALPACA_API_KEY, ALPACA_SECRET, AVAILABLE_SYMBOLS
from alpaca.data.live import StockDataStream

stream = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET)

async def handler(data):
    print(data.timestamp.timestamp())

stream.subscribe_trades(handler, *AVAILABLE_SYMBOLS)
stream.run()