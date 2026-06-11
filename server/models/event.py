from dataclasses import dataclass

from models.candle import Candle

@dataclass
class Event:
    type: str
    symbol: str
    interval: int
    candle: Candle
