#include "matching_engine.hpp"

#include <chrono>


std::vector<Trade>
MatchingEngine::process_order(Order order) {

    if (order.side == "BUY") {

        return match_buy_order(order);

    } else {

        return match_sell_order(order);
    }
}


std::vector<Trade>
MatchingEngine::match_buy_order(
    Order& buy_order
) {

    std::vector<Trade> trades;

    while (buy_order.quantity > 0) {

        double best_ask =
            order_book.get_best_ask();

        if (best_ask < 0) {
            break;
        }

        if (
            buy_order.order_type == "LIMIT"
            && buy_order.price < best_ask
        ) {
            break;
        }

        auto& ask_queue =
            order_book.asks[best_ask];

        Order& sell_order =
            ask_queue.front();

        int traded_quantity = std::min(
            buy_order.quantity,
            sell_order.quantity
        );

        Trade trade;

        trade.buy_order_id =
            buy_order.order_id;

        trade.sell_order_id =
            sell_order.order_id;

        trade.price = best_ask;

        trade.quantity = traded_quantity;

        trade.timestamp =
            std::chrono::duration_cast
            <
                std::chrono::microseconds
            >(
                std::chrono::system_clock
                ::now()
                .time_since_epoch()
            ).count();

        trades.push_back(trade);

        buy_order.quantity -= traded_quantity;

        sell_order.quantity -= traded_quantity;

        if (sell_order.quantity == 0) {

            ask_queue.pop_front();

            if (ask_queue.empty()) {

                order_book.asks.erase(
                    best_ask
                );
            }
        }
    }

    if (
        buy_order.quantity > 0
        && buy_order.order_type == "LIMIT"
    ) {

        order_book.add_order(buy_order);
    }

    return trades;
}


std::vector<Trade>
MatchingEngine::match_sell_order(
    Order& sell_order
) {

    std::vector<Trade> trades;

    while (sell_order.quantity > 0) {

        double best_bid =
            order_book.get_best_bid();

        if (best_bid < 0) {
            break;
        }

        if (
            sell_order.order_type == "LIMIT"
            && sell_order.price > best_bid
        ) {
            break;
        }

        auto& bid_queue =
            order_book.bids[best_bid];

        Order& buy_order =
            bid_queue.front();

        int traded_quantity = std::min(
            sell_order.quantity,
            buy_order.quantity
        );

        Trade trade;

        trade.buy_order_id =
            buy_order.order_id;

        trade.sell_order_id =
            sell_order.order_id;

        trade.price = best_bid;

        trade.quantity = traded_quantity;

        trade.timestamp =
            std::chrono::duration_cast
            <
                std::chrono::microseconds
            >(
                std::chrono::system_clock
                ::now()
                .time_since_epoch()
            ).count();

        trades.push_back(trade);

        sell_order.quantity -= traded_quantity;

        buy_order.quantity -= traded_quantity;

        if (buy_order.quantity == 0) {

            bid_queue.pop_front();

            if (bid_queue.empty()) {

                order_book.bids.erase(
                    best_bid
                );
            }
        }
    }

    if (
        sell_order.quantity > 0
        && sell_order.order_type == "LIMIT"
    ) {

        order_book.add_order(sell_order);
    }

    return trades;
}