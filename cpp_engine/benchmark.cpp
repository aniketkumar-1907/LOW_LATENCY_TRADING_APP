#include <iostream>
#include <vector>
#include <random>
#include <algorithm>

#include "matching_engine.hpp"
#include "timer.hpp"

int main() {

    MatchingEngine engine;

    const int NUM_ORDERS = 1'000'000;

    std::vector<double> latencies;

    latencies.reserve(NUM_ORDERS);

    std::mt19937 rng(42);

    std::uniform_int_distribution<int>
        side_dist(0, 1);

    std::uniform_int_distribution<int>
        quantity_dist(1, 100);

    std::uniform_real_distribution<double>
        price_dist(100.0, 200.0);

    Timer total_timer;

    total_timer.start();

    for (int i = 0; i < NUM_ORDERS; i++) {

        Order order;

        order.symbol = "AAPL";

        order.side =
            side_dist(rng)
            ? "BUY"
            : "SELL";

        order.order_type = "LIMIT";

        order.quantity =
            quantity_dist(rng);

        order.price =
            price_dist(rng);

        order.order_id =
            std::to_string(i);

        order.timestamp = i;

        Timer order_timer;

        order_timer.start();

        engine.process_order(order);

        double latency =
            order_timer.elapsed_us();

        latencies.push_back(latency);
    }

    double total_elapsed =
        total_timer.elapsed_us();

    std::sort(
        latencies.begin(),
        latencies.end()
    );

    double avg_latency = 0;

    for (double l : latencies) {

        avg_latency += l;
    }

    avg_latency /= NUM_ORDERS;

    auto percentile = [&](double p) {

        size_t idx =
            static_cast<size_t>(
                p * NUM_ORDERS
            );

        return latencies[idx];
    };

    double throughput =
        NUM_ORDERS /
        (total_elapsed / 1'000'000.0);

    std::cout << "\n========== C++ BENCHMARK ==========\n";

    std::cout
        << "Orders Processed : "
        << NUM_ORDERS
        << "\n";

    std::cout
        << "Elapsed Time     : "
        << total_elapsed / 1'000'000.0
        << " sec\n";

    std::cout
        << "Throughput       : "
        << throughput
        << " orders/sec\n";

    std::cout
        << "Average Latency  : "
        << avg_latency
        << " us\n";

    std::cout
        << "Median Latency   : "
        << percentile(0.50)
        << " us\n";

    std::cout
        << "P95 Latency      : "
        << percentile(0.95)
        << " us\n";

    std::cout
        << "P99 Latency      : "
        << percentile(0.99)
        << " us\n";

    std::cout
        << "===================================\n";
}