from dataclasses import dataclass

from models.candle import Candle

@dataclass
class Event:
    type: str
    timeframe: int
    candle: Candle
