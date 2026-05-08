cmake_minimum_required(VERSION 3.14)

project(cpp_matching_engine)

set(CMAKE_CXX_STANDARD 17)

find_package(pybind11 REQUIRED)

pybind11_add_module(
    cpp_matching_engine

    bindings.cpp
    matching_engine.cpp
)

add_executable(
    benchmark

    benchmark.cpp
    matching_engine.cpp
)