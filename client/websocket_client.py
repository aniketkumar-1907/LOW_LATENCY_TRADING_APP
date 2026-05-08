import asyncio
import websockets


class ExchangeWebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print(f"Connected to exchange: {self.uri}")

    async def send(self, message: str):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            print("Connection closed")