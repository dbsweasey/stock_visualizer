from fastapi import WebSocket

import logging
logger = logging.getLogger(__name__)

from config import AVAILABLE_INTERVALS

class ConnectionManager:
    def __init__(self):
        self.subscriptions: dict[int, set[WebSocket]] = {
            interval: set()
            for interval in AVAILABLE_INTERVALS
        }
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.subscriptions[5].add(ws)
    
    def subscribe(self, ws, interval):
        logger.info(f"switching to interval {interval}")
        for clients in self.subscriptions.values():
            clients.discard(ws)
        
        self.subscriptions[interval].add(ws)
    
    def disconnect(self, ws: WebSocket):
        for clients in self.subscriptions.values():
            clients.discard(ws)

    async def broadcast(self, timeframe, message):
        # Gather dead connections
        dead = []

        # Send to all connections
        for ws in self.subscriptions[timeframe]:
            try:
                await ws.send_json({
                    "type": message["type"],
                    "candle": message["candle"].__dict__
                })
            except Exception:
                dead.append(ws)
        
        # Disconnect those connections
        for ws in dead:
            self.disconnect(ws)
