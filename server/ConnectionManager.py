from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.subscriptions = {
            1: set(),
            5: set(),
            60: set()
        }
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.subscriptions[5].add(ws)
    
    def subscribe(self, ws, timeframe):
        print(ws, "switching to interval", timeframe)
        for clients in self.subscriptions.values():
            clients.discard(ws)
        
        self.subscriptions[timeframe].add(ws)
    
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
