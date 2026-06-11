import dotenv
import os

dotenv.load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

AVAILABLE_INTERVALS_MAP = [
    {"value": 1, "label": "1s"},
    {"value": 5, "label": "5s"},
    {"value": 15, "label": "15s"},
    {"value": 60, "label": "1m"},
    {"value": 300, "label": "5m"},
    {"value": 900, "label": "15m"},
    {"value": 3600, "label": "1hr"},
]
AVAILABLE_INTERVALS = [i["value"] for i in AVAILABLE_INTERVALS_MAP]

AVAILABLE_SYMBOLS = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META", "TSLA"]