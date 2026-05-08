#pragma once

#include <vector>

#include "order_book.hpp"
#include "trade.hpp"

class MatchingEngine {

private:

    OrderBook order_book;

public:

    std::vector<Trade> process_order(
        Order order
    );

    std::vector<Trade> match_buy_order(
        Order& buy_order
    );

    std::vector<Trade> match_sell_order(
        Order& sell_order
    );
};