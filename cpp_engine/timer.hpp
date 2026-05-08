#pragma once

#include <chrono>

class Timer {

private:

    std::chrono::high_resolution_clock::time_point start_time;

public:

    void start() {

        start_time =
            std::chrono::high_resolution_clock::now();
    }

    double elapsed_us() {

        auto end_time =
            std::chrono::high_resolution_clock::now();

        return std::chrono::duration<double,
            std::micro>(
                end_time - start_time
            ).count();
    }
};