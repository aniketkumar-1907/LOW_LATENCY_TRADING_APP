import asyncio
import random
import struct
import time
import uuid

import msgpack

from benchmark.latency_metrics import LatencyMetrics


HOST = "127.0.0.1"
PORT = 9000

metrics = LatencyMetrics()


# =========================
# Framing Helpers
# =========================

async def send_message(writer, message):

    payload = msgpack.packb(message)

    header = struct.pack(
        "!I",
        len(payload)
    )

    writer.write(header + payload)

    await writer.drain()


async def receive_message(reader):

    header = await reader.readexactly(4)

    message_length = struct.unpack(
        "!I",
        header
    )[0]

    payload = await reader.readexactly(
        message_length
    )

    return msgpack.unpackb(
        payload,
        raw=False
    )


class TCPBenchmarkClient:

    def __init__(self):

        self.reader = None
        self.writer = None

        self.pending_orders = {}

        self.receiver_task = None

    async def connect(self):

        self.reader, self.writer = (
            await asyncio.open_connection(
                HOST,
                PORT
            )
        )

        print(
            f"Connected to TCP exchange "
            f"{HOST}:{PORT}"
        )

        self.receiver_task = asyncio.create_task(
            self.receive_loop()
        )

    async def receive_loop(self):

        try:

            while True:

                data = await receive_message(
                    self.reader
                )

                if data.get("type") == "ACK":

                    order_id = data["order_id"]

                    if (
                        order_id
                        in self.pending_orders
                    ):

                        send_time = (
                            self.pending_orders.pop(
                                order_id
                            )
                        )

                        latency_us = (
                            time.perf_counter_ns()
                            - send_time
                        ) / 1000

                        metrics.record(latency_us)

        except asyncio.IncompleteReadError:
            pass

    async def send_order(self, order):

        self.pending_orders[
            order["order_id"]
        ] = time.perf_counter_ns()

        await send_message(
            self.writer,
            order
        )

    async def close(self):

        await asyncio.sleep(1)

        if self.receiver_task:
            self.receiver_task.cancel()

        self.writer.close()

        await self.writer.wait_closed()


def generate_order(symbol="AAPL"):

    side = random.choice([
        "BUY",
        "SELL"
    ])

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