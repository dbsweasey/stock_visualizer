from fastapi import WebSocket
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)

from config import AVAILABLE_INTERVALS

from models.event import Event

class ConnectionManager:
    """ Holds a table of connections (called subscriptions), each one referring to specific interval and symbol combination

    Implements:
        connect(): given a WebSocket, establishes an initial connection to the client

        subscribe(): adds the WebSocket to the subscription set for the symbol and interval, allowing the
        client to receiving continuous updates

        broadcast(): broadcasts a specific event to all relevant subscribers

        disconnect(): gracefully handles client disconnect and removes from subscriber set

    """
    def __init__(self):
        self.subscriptions: dict[str, dict[int, set[WebSocket]]] = (
            defaultdict(
                lambda: {
                    interval: set() for interval in AVAILABLE_INTERVALS
                }
            )
        )
    
    async def connect(self, ws: WebSocket):
        """ Connects client and establishes initial subscription (AAPL, 5s)
        
        Args:
            ws (WebSocket): WebSocket object to connect
        """
        await ws.accept()
        self.subscriptions["AAPL"][5].add(ws)
    
    def subscribe(self, ws: WebSocket, symbol: str, interval: int):
        """ Adds the WebSocket to the subscription table with the keys
        'symbol' and 'interval'

        Args:
            ws (WebSocket): WebSocket object to connect

            symbol (str): Symbol to subscribe to

            interval (int): Interval to subscribe to 
        """
        logger.info(f"Subscribing to {symbol}: {interval}")

        
        self.subscriptions[symbol][interval].add(ws)
    
    def unsubscribe(self, ws: WebSocket, symbol: str, interval: int):
        logger.info(f"Unsubscribing from {symbol}: {interval}")

        self.subscriptions[symbol][interval].remove(ws)

    def disconnect(self, ws: WebSocket):
        """ Disconnects WebSocket from all subscriptions

        Args:
            ws (WebSocket): the WebSocket to disconnect
        """
        for s in self.subscriptions.values():
            for clients in s.values():
                clients.discard(ws)

    async def broadcast(self, event: Event):
        """ Broadcasts an event to all clients subscribed to its symbol, interval.

        Args:
            event (Event): Event object containing candle data, symbol, and interval to send
            to client
        """
        # Gather dead connections
        dead = []
        # Send to all connections
        for ws in self.subscriptions[event.symbol][event.interval]:
            try:
                await ws.send_json({
                    "type": event.type,
                    "symbol": event.symbol,
                    "interval": event.interval,
                    "candle": event.candle.__dict__
                })
            except Exception:
                dead.append(ws)
        
        # Disconnect those connections
        for ws in dead:
            self.disconnect(ws)
