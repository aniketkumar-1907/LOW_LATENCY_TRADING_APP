import asyncio
import struct
import msgpack
import sys

from exchange.engine.order import Order
from exchange.engine.enums import MessageType
from exchange.engine.ring_buffer import RingBuffer

# =========================
# Load C++ Engine
# =========================

sys.path.append(
    "cpp_engine/build"
)

from cpp_matching_engine import (
    MatchingEngine,
    Order as CppOrder
)

matching_engine = MatchingEngine()

# =========================
# Connected Clients
# =========================

clients = set()

# =========================
# Market Data Ring Buffer
# =========================

market_data_queue = RingBuffer(
    100000
)

# =========================
# Message Framing Helpers
# =========================

async def send_message(
    writer,
    message
):

    payload = msgpack.packb(message)

    header = struct.pack(
        "!I",
        len(payload)
    )

    writer.write(
        header + payload
    )

    await writer.drain()


async def receive_message(reader):

    # Read 4-byte length header
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

# =========================
# Broadcaster
# =========================

async def broadcaster():

    while True:

        message = market_data_queue.pop()

        if message is None:

            await asyncio.sleep(0)

            continue

        disconnected = []

        for writer in clients:

            try:

                await send_message(
                    writer,
                    message
                )

            except Exception:

                disconnected.append(
                    writer
                )

        for writer in disconnected:

            clients.discard(writer)

# =========================
# Python -> C++ Order
# =========================

def to_cpp_order(order):

    cpp_order = CppOrder()

    cpp_order.symbol = order.symbol

    cpp_order.side = order.side

    cpp_order.order_type = (
        order.order_type
    )

    cpp_order.quantity = (
        order.quantity
    )

    cpp_order.price = (
        order.price
        if order.price is not None
        else 0.0
    )

    cpp_order.order_id = (
        order.order_id
    )

    cpp_order.timestamp = (
        order.timestamp
    )

    return cpp_order

# =========================
# Client Handler
# =========================

async def handle_client(
    reader,
    writer
):

    clients.add(writer)

    addr = writer.get_extra_info(
        "peername"
    )

    print(
        f"Trader connected: {addr}"
    )

    try:

        while True:

            data = await receive_message(
                reader
            )

            message_type = data.get(
                "type",
                "NEW_ORDER"
            )

            # =========================
            # NEW ORDER
            # =========================

            if (
                message_type
                == MessageType.NEW_ORDER.value
            ):

                # Python order
                order = Order(
                    symbol=data["symbol"],
                    side=data["side"],
                    order_type=data[
                        "order_type"
                    ],
                    quantity=data[
                        "quantity"
                    ],
                    price=data.get(
                        "price"
                    ),
                    order_id=data[
                        "order_id"
                    ],
                    timestamp=data[
                        "timestamp"
                    ]
                )

                # Convert to C++ order
                cpp_order = to_cpp_order(
                    order
                )

                # Native matching engine
                trades = (
                    matching_engine
                    .process_order(
                        cpp_order
                    )
                )

                # =========================
                # ACK
                # =========================

                ack = {
                    "type": "ACK",
                    "order_id": (
                        order.order_id
                    ),
                    "status": "ACCEPTED"
                }

                await send_message(
                    writer,
                    ack
                )

                # =========================
                # Trade Broadcasts
                # =========================

                for trade in trades:

                    trade_message = {
                        "type": "TRADE",

                        "buy_order_id":
                        trade.buy_order_id,

                        "sell_order_id":
                        trade.sell_order_id,

                        "price":
                        trade.price,

                        "quantity":
                        trade.quantity,

                        "timestamp":
                        trade.timestamp
                    }

                    market_data_queue.push(
                        trade_message
                    )

                # =========================
                # NOTE:
                # Market updates removed
                # temporarily because
                # C++ engine currently
                # does not expose
                # order book state.
                # =========================

            # =========================
            # CANCEL ORDER
            # =========================

            elif (
                message_type
                == MessageType.CANCEL_ORDER.value
            ):

                # Not implemented yet
                response = {
                    "type":
                    "CANCEL_ACK",

                    "order_id":
                    data["order_id"],

                    "success":
                    False
                }

                await send_message(
                    writer,
                    response
                )

    except asyncio.IncompleteReadError:

        print(
            f"Trader disconnected: {addr}"
        )

    except Exception as e:

        print(
            f"Client error: {e}"
        )

    finally:

        clients.discard(writer)

        writer.close()

        await writer.wait_closed()

# =========================
# Main Server
# =========================

async def main():

    asyncio.create_task(
        broadcaster()
    )

    server = await asyncio.start_server(
        handle_client,
        "127.0.0.1",
        9000
    )

    print(
        "TCP Exchange running on "
        "127.0.0.1:9000"
    )

    async with server:

        await server.serve_forever()

# =========================
# Entry Point
# =========================

if __name__ == "__main__":

    asyncio.run(main())