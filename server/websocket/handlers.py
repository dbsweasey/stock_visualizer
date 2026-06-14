from fastapi import WebSocket, WebSocketDisconnect

import logging
logger = logging.getLogger(__name__)

class WebSocketHandler:
    """ Handles communication between client and server through a single websocket.
    
    Receives direct communication from client and passes messages through architecture to
    fulfil request. 

    Sends messages to a specific client.

    Args:
        manager (ConnectionManager): Connection manager to store all WebSocket connections

        engine (CandleEngine): Required to connect the WebSocket comm. channel to candle architecture
    """
    def __init__(self, manager, engine):
        self.manager = manager
        self.engine = engine

    async def send_snapshot(self, ws: WebSocket, symbol: str, interval: int):
        """ Sends the candle history for a given symbol and history to the client

        Args:
            ws (WebSocket): The WebSocket to send to

            symbol (str): The symbol to get the snapshot of

            interval (int): The interval to get the snapshot of
        """
        logger.info(f"Sending snapshot of {symbol}: {interval}")
        candles = self.engine.get_history(symbol, interval)

        await ws.send_json({
            "type": "snapshot",
            "symbol": symbol,
            "interval": interval,
            "candles": [c.__dict__ for c in candles]
        })

    # TODO: Restructure to "subscribe" and "unsubscribe"
    async def handle_message(self, ws: WebSocket, msg: dict):
        """ Handles messages from the client, based on message type

        Args:
            ws (WebSocket): the WebSocket from which the message came

            msg (dict): The JSON message
        """

        logger.info(f"Received message: {msg}")
        msg_type = msg.get("type")

        # Current subscribe message. Will be updated
        if msg_type == "subscribe":
            interval = msg["interval"]
            symbol = msg["symbol"]
            logger.info(f"Received request to subscribe to {symbol}:{interval}")

            self.manager.subscribe(ws, symbol, interval)
            await self.send_snapshot(ws, symbol, interval)
        
        if msg_type == "unsubscribe":
            interval = msg["interval"]
            symbol = msg["symbol"]
            logger.info(f"Received request to unsubscribe from {symbol}:{interval}")

            self.manager.unsubscribe(ws, symbol, interval)
    
    async def handle_connection(self, ws: WebSocket):
        """ Establishes initial connection with client

        Args:
            ws (WebSocket): The client WebSocket to connect to
        """
        logger.info("Creating websocket...")
        
        # Calling manager to add this ws to subscriptions
        await self.manager.connect(ws)

        try:
            # First snapshot, subscribe to APPL, 5 by default
            await self.send_snapshot(ws, "AAPL", 5)

            # Event loop, wait for message, then handle
            while True:
                msg = await ws.receive_json()
                await self.handle_message(ws, msg)
        
        except WebSocketDisconnect:
            self.manager.disconnect(ws)

