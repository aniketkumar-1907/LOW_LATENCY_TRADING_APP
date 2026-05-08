import asyncio

from benchmark.tcp_benchmark_client import (
    TCPBenchmarkClient,
    generate_order,
    metrics
)


TOTAL_ORDERS = 5000
CONCURRENT_CLIENTS = 5


async def run_client(client_id, orders_per_client):

    client = TCPBenchmarkClient()

    await client.connect()

    tasks = []

    for _ in range(orders_per_client):

        order = generate_order()

        task = asyncio.create_task(
            client.send_order(order)
        )

        tasks.append(task)

    await asyncio.gather(*tasks)

    print(f"Client {client_id} finished")

    await client.close()


async def main():

    orders_per_client = (
        TOTAL_ORDERS // CONCURRENT_CLIENTS
    )

    tasks = []

    for client_id in range(
        CONCURRENT_CLIENTS
    ):

        task = asyncio.create_task(
            run_client(
                client_id,
                orders_per_client
            )
        )

        tasks.append(task)

    await asyncio.gather(*tasks)

    await asyncio.sleep(2)

    metrics.report()


if __name__ == "__main__":
    asyncio.run(main())