import asyncio
import msgpack
import websockets

from exchange.engine.order import Order
from exchange.engine.matching_engine import MatchingEngine
from exchange.engine.enums import MessageType


clients = set()

matching_engine = MatchingEngine()

# Async queue for market data broadcasting
market_data_queue = asyncio.Queue()


async def broadcaster():

    while True:

        message = await market_data_queue.get()

        disconnected_clients = set()

        packed_message = msgpack.packb(message)

        for client in clients:

            try:
                await client.send(packed_message)

            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)

        clients.difference_update(disconnected_clients)

        market_data_queue.task_done()


async def handle_client(websocket):

    clients.add(websocket)

    print("Trader connected")

    try:

        async for message in websocket:

            data = msgpack.unpackb(message, raw=False)

            message_type = data.get("type", "NEW_ORDER")

            # NEW ORDER
            if message_type == MessageType.NEW_ORDER.value:

                order = Order(
                    symbol=data["symbol"],
                    side=data["side"],
                    order_type=data["order_type"],
                    quantity=data["quantity"],
                    price=data.get("price"),
                    order_id=data["order_id"],
                    timestamp=data["timestamp"]
                )

                trades = matching_engine.process_order(order)

                # ACK directly to sender
                ack = {
                    "type": "ACK",
                    "order_id": order.order_id,
                    "status": "ACCEPTED"
                }

                await websocket.send(
                    msgpack.packb(ack)
                )

                # Queue trade broadcasts
                for trade in trades:

                    trade_message = {
                        "type": "TRADE",
                        "buy_order_id": trade.buy_order_id,
                        "sell_order_id": trade.sell_order_id,
                        "price": trade.price,
                        "quantity": trade.quantity,
                        "timestamp": trade.timestamp
                    }

                    await market_data_queue.put(
                        trade_message
                    )

                # Queue market update
                order_book = matching_engine.get_order_book(
                    order.symbol
                )

                market_update = {
                    "type": "MARKET_UPDATE",
                    "symbol": order.symbol,
                    "best_bid": order_book.get_best_bid(),
                    "best_ask": order_book.get_best_ask()
                }

                await market_data_queue.put(
                    market_update
                )

            # CANCEL ORDER
            elif message_type == MessageType.CANCEL_ORDER.value:

                success = matching_engine.cancel_order(
                    data["order_id"]
                )

                response = {
                    "type": "CANCEL_ACK",
                    "order_id": data["order_id"],
                    "success": success
                }

                await websocket.send(
                    msgpack.packb(response)
                )

    except websockets.exceptions.ConnectionClosed:
        print("Trader disconnected")

    finally:
        clients.discard(websocket)


async def main():

    # Start broadcaster task
    asyncio.create_task(broadcaster())

    server = await websockets.serve(
        handle_client,
        "localhost",
        8080,
        max_queue=None
    )

    print("Exchange Gateway running on ws://localhost:8080")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())