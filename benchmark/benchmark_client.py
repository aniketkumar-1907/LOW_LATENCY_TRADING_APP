import asyncio
import random
import time
import uuid

import msgpack
import websockets

from benchmark.latency_metrics import LatencyMetrics


EXCHANGE_URI = "ws://localhost:8080"

metrics = LatencyMetrics()


class BenchmarkClient:

    def __init__(self, uri):

        self.uri = uri
        self.websocket = None

        self.pending_orders = {}

        self.receiver_task = None

    async def connect(self):

        self.websocket = await websockets.connect(
            self.uri,
            max_queue=None
        )

        print(f"Connected to exchange: {self.uri}")

        # Dedicated receiver loop
        self.receiver_task = asyncio.create_task(
            self.receive_messages()
        )

    async def receive_messages(self):

        try:

            async for response in self.websocket:

                data = msgpack.unpackb(
                    response,
                    raw=False
                )

                # Process ACKs only
                if data.get("type") == "ACK":

                    order_id = data.get("order_id")

                    if order_id in self.pending_orders:

                        send_time = self.pending_orders.pop(
                            order_id
                        )

                        receive_time = (
                            time.perf_counter_ns()
                        )

                        latency_us = (
                            receive_time - send_time
                        ) / 1000

                        metrics.record(latency_us)

        except websockets.exceptions.ConnectionClosed:
            pass

    async def send_order(self, order):

        self.pending_orders[order["order_id"]] = (
            time.perf_counter_ns()
        )

        await self.websocket.send(
            msgpack.packb(order)
        )

    async def close(self):

        # Allow final ACK processing
        await asyncio.sleep(1)

        if self.receiver_task:
            self.receiver_task.cancel()

        await self.websocket.close()


def generate_order(symbol="AAPL"):

    side = random.choice(["BUY", "SELL"])

    order_type = random.choice([
        "LIMIT",
        "MARKET"
    ])

    price = None

    if order_type == "LIMIT":
        price = round(
            random.uniform(100, 200),
            2
        )

    return {
        "type": "NEW_ORDER",
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": random.randint(1, 100),
        "price": price,
        "order_id": str(uuid.uuid4()),
        "timestamp": int(
            time.time() * 1_000_000
        )
    }