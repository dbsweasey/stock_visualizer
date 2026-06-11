from fastapi import WebSocket
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)

from config import AVAILABLE_INTERVALS
from models.event import Event

class ConnectionManager:
    def __init__(self):
        self.subscriptions: dict[str, dict[int, set[WebSocket]]] = (
            defaultdict(
                lambda: {
                    interval: set() for interval in AVAILABLE_INTERVALS
                }
            )
        )
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.subscriptions["AAPL"][5].add(ws)
    
    def subscribe(self, ws, symbol: str, interval: int):
        logger.info(f"Subscribing to {symbol}: {interval}")
        for s in self.subscriptions.values():
            for clients in s.values():
                clients.discard(ws)
        
        self.subscriptions[symbol][interval].add(ws)
    
    def disconnect(self, ws: WebSocket):
        for s in self.subscriptions.values():
            for clients in s.values():
                clients.discard(ws)

    async def broadcast(self, event):
        # Gather dead connections
        dead = []
        # Send to all connections
        for ws in self.subscriptions[event.symbol][event.interval]:
            try:
                await ws.send_json({
                    "type": event.type,
                    "candle": event.candle.__dict__
                })
            except Exception:
                dead.append(ws)
        
        # Disconnect those connections
        for ws in dead:
            self.disconnect(ws)
