import asyncio
import json
import websockets


clients = set()


async def handle_client(websocket):
    clients.add(websocket)

    print("Trader connected")

    try:
        async for message in websocket:
            order = json.loads(message)

            print(f"Received Order: {order}")

            ack = {
                "type": "ACK",
                "order_id": order["order_id"],
                "status": "ACCEPTED"
            }

            await websocket.send(json.dumps(ack))

            market_update = {
                "type": "MARKET_UPDATE",
                "symbol": order["symbol"],
                "best_bid": 150.20,
                "best_ask": 150.30
            }

            for client in clients:
                await client.send(json.dumps(market_update))

    except websockets.exceptions.ConnectionClosed:
        print("Trader disconnected")

    finally:
        clients.remove(websocket)


async def main():
    server = await websockets.serve(handle_client, "localhost", 8080)

    print("Mock exchange running on ws://localhost:8080")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())