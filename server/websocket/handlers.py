from fastapi import WebSocket, WebSocketDisconnect

import logging
logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self, manager, engine):
        self.manager = manager
        self.engine = engine

    async def send_snapshot(self, ws: WebSocket, symbol: str, interval: int):
        logger.info(f"Sending snapshot of {symbol}: {interval}")
        candles = self.engine.get_history(symbol, interval)

        await ws.send_json({
            "type": "snapshot",
            "candles": [c.__dict__ for c in candles]
        })

    async def handle_message(self, ws: WebSocket, msg: dict):
        logger.info(f"Received message: {msg}")
        msg_type = msg.get("type")

        if msg_type == "update_interval":
            interval = msg["interval"]
            symbol = msg["symbol"]
            logger.info(f"Received request to switch interval to {interval}")

            self.manager.subscribe(ws, symbol, interval)
            await self.send_snapshot(ws, symbol, interval)
    
    async def handle_connection(self, ws: WebSocket):
        logger.info("Creating websocket...")
        await self.manager.connect(ws)

        try:
            # First snapshot, subscribe at 5 by default
            await self.send_snapshot(ws, "AAPL", 5)

            while True:
                msg = await ws.receive_json()
                await self.handle_message(ws, msg)
        
        except WebSocketDisconnect:
            self.manager.disconnect(ws)

