import asyncio


async def listen_for_market_updates(client):
    while True:
        try:
            message = await client.receive()
            print(f"MARKET UPDATE: {message}")

        except Exception as e:
            print(f"Connection lost: {e}")
            break