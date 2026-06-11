from dataclasses import dataclass

@dataclass
class Tick:
    price: float
    symbol: str
    timestamp: float