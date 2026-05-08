import asyncio
import time

from benchmark.benchmark_client import (
    BenchmarkClient,
    generate_order,
    metrics,
    EXCHANGE_URI
)


TOTAL_ORDERS = 5000
CONCURRENT_CLIENTS = 5


async def run_client(client_id, orders_per_client):

    client = BenchmarkClient(EXCHANGE_URI)

    await client.connect()

    start = time.perf_counter()

    # PIPELINED sending
    tasks = []

    for _ in range(orders_per_client):

        order = generate_order()

        task = asyncio.create_task(
            client.send_order(order)
        )

        tasks.append(task)

    # Wait for all sends to complete
    await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    print(
        f"Client {client_id} finished "
        f"in {elapsed:.2f}s"
    )

    await client.close()


async def main():

    orders_per_client = (
        TOTAL_ORDERS // CONCURRENT_CLIENTS
    )

    tasks = []

    for client_id in range(CONCURRENT_CLIENTS):

        task = asyncio.create_task(
            run_client(client_id, orders_per_client)
        )

        tasks.append(task)

    await asyncio.gather(*tasks)

    # Wait for remaining ACKs
    await asyncio.sleep(2)

    metrics.report()


if __name__ == "__main__":
    asyncio.run(main())