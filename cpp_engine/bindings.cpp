#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "matching_engine.hpp"

namespace py = pybind11;


PYBIND11_MODULE(cpp_matching_engine, m) {

    py::class_<Order>(m, "Order")

        .def(py::init<>())

        .def_readwrite(
            "symbol",
            &Order::symbol
        )

        .def_readwrite(
            "side",
            &Order::side
        )

        .def_readwrite(
            "order_type",
            &Order::order_type
        )

        .def_readwrite(
            "quantity",
            &Order::quantity
        )

        .def_readwrite(
            "price",
            &Order::price
        )

        .def_readwrite(
            "order_id",
            &Order::order_id
        )

        .def_readwrite(
            "timestamp",
            &Order::timestamp
        );

    py::class_<Trade>(m, "Trade")

        .def_readwrite(
            "buy_order_id",
            &Trade::buy_order_id
        )

        .def_readwrite(
            "sell_order_id",
            &Trade::sell_order_id
        )

        .def_readwrite(
            "price",
            &Trade::price
        )

        .def_readwrite(
            "quantity",
            &Trade::quantity
        )

        .def_readwrite(
            "timestamp",
            &Trade::timestamp
        );

    py::class_<MatchingEngine>(
        m,
        "MatchingEngine"
    )

        .def(py::init<>())

        .def(
            "process_order",
            &MatchingEngine::process_order
        );
}