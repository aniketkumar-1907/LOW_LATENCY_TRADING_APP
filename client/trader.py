import asyncio

from order import Order, Side, OrderType
from websocket_client import ExchangeWebSocketClient
from market_listener import listen_for_market_updates


EXCHANGE_URI = "ws://localhost:8080"


async def main():
    client = ExchangeWebSocketClient(EXCHANGE_URI)

    await client.connect()

    listener_task = asyncio.create_task(
        listen_for_market_updates(client)
    )

    buy_order = Order(
        symbol="AAPL",
        side=Side.BUY.value,
        order_type=OrderType.LIMIT.value,
        quantity=100,
        price=150.25,
    )

    await client.send(buy_order.to_json())

    print(f"Sent BUY Order: {buy_order.to_json()}")

    await asyncio.sleep(2)

    sell_order = Order(
        symbol="AAPL",
        side=Side.SELL.value,
        order_type=OrderType.MARKET.value,
        quantity=50,
    )
    
    await client.send(sell_order.to_json())

    print(f"Sent SELL Order: {sell_order.to_json()}")

    await asyncio.sleep(30)

    listener_task.cancel()

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())