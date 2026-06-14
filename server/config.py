import dotenv
import os

dotenv.load_dotenv()

# Frontend port and address
PORT = os.getenv("PORT")
ADDRESS = os.getenv("ADDRESS")

# Alpaca creds for live market data
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

# Supported intervals, and their labels for the frontend
AVAILABLE_INTERVALS_MAP = [
    {"value": 1, "label": "1s"},
    {"value": 5, "label": "5s"},
    {"value": 15, "label": "15s"},
    {"value": 60, "label": "1m"},
    {"value": 300, "label": "5m"},
    {"value": 900, "label": "15m"},
    {"value": 3600, "label": "1hr"},
]
# AVAILABLE_INTERVALS_MAP = [
#     {"value": 1, "label": "1s"},
#     {"value": 5, "label": "5s"},
# ]

# Pure numbers, for backend use
AVAILABLE_INTERVALS = [i["value"] for i in AVAILABLE_INTERVALS_MAP]

# Available symbols
AVAILABLE_SYMBOLS = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META", "TSLA"]

# AVAILABLE_SYMBOLS = ["AAPL"]