#pragma once

#include <map>
#include <deque>
#include <vector>

#include "order.hpp"

class OrderBook {

public:

    // BUY side descending
    std::map<
        double,
        std::deque<Order>,
        std::greater<double>
    > bids;

    // SELL side ascending
    std::map<
        double,
        std::deque<Order>
    > asks;

    void add_order(const Order& order) {

        if (order.side == "BUY") {

            bids[order.price].push_back(order);

        } else {

            asks[order.price].push_back(order);
        }
    }

    double get_best_bid() {

        if (bids.empty()) {
            return -1;
        }

        return bids.begin()->first;
    }

    double get_best_ask() {

        if (asks.empty()) {
            return -1;
        }

        return asks.begin()->first;
    }
};