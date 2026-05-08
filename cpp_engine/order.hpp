#pragma once

#include <string>

struct Order {

    std::string symbol;

    std::string side;

    std::string order_type;

    int quantity;

    double price;

    std::string order_id;

    long timestamp;
};