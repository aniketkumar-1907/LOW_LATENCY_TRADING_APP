# Low-Latency Exchange Engine

## Overview

This project started as an exploration into:
- Quant Developer systems
- Low-latency exchange infrastructure
- Matching engine architecture
- Order book design
- Native performance optimization
- Python ↔ C++ interoperability

The goal was to progressively evolve a simple trading simulator into a realistic low-latency exchange core similar to the systems used inside proprietary trading firms, exchanges, and HFT infrastructure.

---

# Project Evolution

The system evolved through multiple architectural stages.

---

# Stage 1 — Basic WebSocket Exchange

## Goal

Build a simple exchange simulator capable of:
- Accepting orders
- Matching buy/sell orders
- Broadcasting trades
- Maintaining an order book

---

## Architecture

```text
Trading Client
      ↓
WebSocket Gateway
      ↓
Python Matching Engine
      ↓
Order Book
```

---

## Components Built

### Trading Client

- WebSocket-based trading client
- Sends:
  - LIMIT orders
  - MARKET orders
- Receives:
  - ACKs
  - Trades
  - Market updates

---

### Matching Engine

Implemented:
- Price-time priority
- BUY/SELL matching
- MARKET orders
- LIMIT orders
- Trade generation

---

### Order Book

Built using:
- `dict`
- `deque`

Features:
- Best bid/ask tracking
- FIFO matching
- Multiple price levels

---

## Initial Example Flow

### BUY LIMIT Order

```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "order_type": "LIMIT",
  "quantity": 100,
  "price": 150.25
}
```

### SELL MARKET Order

```json
{
  "symbol": "AAPL",
  "side": "SELL",
  "order_type": "MARKET",
  "quantity": 50
}
```

### Generated Trade

```json
{
  "type": "TRADE",
  "price": 150.25,
  "quantity": 50
}
```

---

# Stage 2 — Benchmarking Infrastructure

## Goal

Measure:
- Throughput
- Average latency
- Tail latency
- System stability

---

## Benchmark Architecture

```text
Benchmark Clients
        ↓
WebSocket Exchange
        ↓
Matching Engine
```

---

## Metrics Collected

- Orders/sec
- Average latency
- Median latency
- P95 latency
- P99 latency

---

# Stage 3 — Python Optimization Pass

## Optimizations Added

### Ring Buffer

Implemented custom ring buffer for:
- Market data broadcasting
- Reduced allocation overhead
- Faster producer-consumer flow

---

### Object Pooling

Trade object pool introduced to:
- Reduce garbage collection pressure
- Reuse trade objects
- Improve allocator behavior

---

### Order Registry

Added:
- O(1) order lookup
- Cancel order support

---

### TCP Transport

Replaced WebSockets with raw TCP sockets.

Reason:
- Lower protocol overhead
- Better latency characteristics
- More realistic exchange transport

---

# TCP Architecture

```text
Trading Client
      ↓
TCP Gateway
      ↓
Matching Engine
      ↓
Order Book
```

---

# Binary Message Framing

Implemented:
- Fixed-size headers
- Length-prefixed packets
- `msgpack` serialization

---

# Python Benchmark Results

## Initial Python Version

```text
Orders Processed : 5000
Elapsed Time     : 3.26 sec
Throughput       : 1532.90 orders/sec
Average Latency  : 240446.77 us
Median Latency   : 250013.73 us
P95 Latency      : 267369.58 us
P99 Latency      : 267448.46 us
```

---

## Optimized Python TCP Version

```text
Orders Processed : 5000
Elapsed Time     : 3.08 sec
Throughput       : 1621.15 orders/sec
Average Latency  : 45454.81 us
Median Latency   : 46380.96 us
P95 Latency      : 59839.75 us
P99 Latency      : 60765.75 us
```

---

# Observations

Python optimizations significantly improved latency.

Main bottlenecks identified:
- Python interpreter overhead
- asyncio overhead
- object allocations
- serialization costs
- networking overhead

---

# Stage 4 — Native C++ Matching Engine

## Goal

Move performance-critical matching logic into native C++.

---

# New Hybrid Architecture

```text
Python TCP Gateway
        ↓
C++ Matching Engine
        ↓
C++ Order Book
```

---

## Technologies Introduced

### C++17

Used for:
- Native performance
- Deterministic memory behavior
- Cache-efficient data structures

---

### pybind11

Used to expose:
- C++ MatchingEngine
- C++ Order
- C++ Trade

Directly into Python.

---

### CMake

Used for:
- Native compilation
- Module generation
- Build management

---

# Native Components

Implemented in C++:

- Matching engine
- Order book
- Trade generation
- Price-time priority matching

---

# C++ Data Structures

## Order Book

Used:

```cpp
std::map<double, std::deque<Order>>
```

Features:
- Sorted price levels
- FIFO execution
- Bid/ask separation

---

# Hybrid Benchmark Results

## Python Gateway + C++ Matching Engine

```text
Orders Processed : 5000
Elapsed Time     : 3.07 sec
Throughput       : 1628.01 orders/sec
Average Latency  : 69693.12 us
Median Latency   : 64607.62 us
P95 Latency      : 106685.21 us
P99 Latency      : 110599.71 us
```

---

# Important Discovery

The hybrid architecture performed WORSE than optimized Python.

Reason:
- Python ↔ C++ interop overhead
- Object marshaling costs
- Boundary crossing overhead
- Serialization still handled in Python

---

# Key Systems Engineering Lesson

## Amdahl's Law

Optimizing only a small part of the system does not necessarily improve overall performance.

The true bottleneck was still:
- Python networking
- Serialization
- asyncio runtime

NOT matching logic.

---

# Stage 5 — Pure Native C++ Benchmark

## Goal

Benchmark ONLY the matching engine.

Remove:
- Python
- TCP
- Serialization
- pybind11
- asyncio

---

# Pure Native Benchmark Architecture

```text
Synthetic Orders
        ↓
C++ Matching Engine
        ↓
Latency Measurement
```

---

# Benchmark Design

Generated:
- 1,000,000 synthetic orders
- Random BUY/SELL distribution
- Random quantities
- Random prices

Measured:
- Per-order latency
- Total throughput
- Tail latency

---

# Pure C++ Benchmark Results

```text
========== C++ BENCHMARK ==========
Orders Processed : 1000000
Elapsed Time     : 1.69387 sec
Throughput       : 590366 orders/sec
Average Latency  : 1.21736 us
Median Latency   : 0.792 us
P95 Latency      : 2.75 us
P99 Latency      : 4.583 us
===================================
```

---

# Final Performance Analysis

## Comparison Across Architectures

| Architecture | Orders Processed | Median Latency |
|---|---:|---:|
| Python asyncio | 5000 | ~250ms |
| Optimized Python TCP | 5000 | ~46ms |
| Python + C++ Hybrid | 5000 | ~64ms |
| Pure Native C++ | 1,000,000 | ~0.79µs |

### Latency Improvement Chart

```text
Latency (lower is better)

Python asyncio        | ███████████████████████████████████████████████████ 250ms (5000 orders)
Optimized Python TCP  | ████████ 46ms (5000 orders)
Python + C++ Hybrid   | █████████ 64ms (5000 orders)
Pure Native C++       | ░ 0.79µs (1,000,000 orders)
```

> The chart shows the relative latency improvement and workload size across each architecture stage.

---

# Key Findings

## Python Was The Main Bottleneck

Pure native C++ demonstrated:
- Sub-microsecond latency
- Stable tail latency
- High throughput
- Excellent scaling characteristics

---

## Tail Latency Stability

P99 latency:

```text
4.583 us
```

This indicates:
- Healthy allocator behavior
- Good cache locality
- Predictable execution path
- Minimal stalls

---

# Core Concepts Learned

This project covered:

## Exchange Infrastructure

- Matching engines
- Order books
- Market data distribution
- Trade execution

---

## Low-Latency Systems

- TCP transport
- Binary protocols
- Ring buffers
- Object pooling
- Memory reuse
- Tail latency analysis

---

## Native Performance Engineering

- C++17
- pybind11 interoperability
- Native benchmarking
- Runtime overhead analysis
- FFI costs
- Amdahl’s Law

---

## Benchmarking Methodology

- Throughput analysis
- Median latency
- P95/P99 analysis
- Synthetic workload generation
- Bottleneck isolation

---

# Current System Architecture

## Pure Native Benchmark

```text
Benchmark Driver
        ↓
Matching Engine
        ↓
Order Book
```

---

# Repository Structure

```text
Trading App/
│
├── exchange/
│   ├── engine/
│   ├── gateway/
│   └── client/
│
├── benchmark/
│
├── cpp_engine/
│   ├── order.hpp
│   ├── trade.hpp
│   ├── order_book.hpp
│   ├── matching_engine.hpp
│   ├── matching_engine.cpp
│   ├── bindings.cpp
│   ├── benchmark.cpp
│   ├── timer.hpp
│   └── CMakeLists.txt
│
└── test_cpp_engine.py
```

---

# Future Work

The current implementation is intentionally simplified.

Potential future improvements include:

---

## 1. Price Ladder Order Book

Replace:

```cpp
std::map
```

with:

```cpp
contiguous price arrays
```

Benefits:
- Better cache locality
- Reduced pointer chasing
- Lower branch misprediction
- Predictable memory access

---

## 2. Lock-Free Queues

Implement:
- SPSC queues
- MPMC queues
- Wait-free message passing

---

## 3. Memory Arenas

Replace heap allocations with:
- arena allocators
- slab allocators
- fixed-size pools

---

## 4. Dedicated Matching Threads

Introduce:
- CPU pinning
- isolated cores
- NUMA awareness

---

## 5. Binary Native Protocol

Replace `msgpack` with:
- fixed-size binary structs
- zero-copy serialization
- SIMD-friendly parsing

---

## 6. Full Native Exchange

Move:
- TCP server
- serialization
- market data broadcasting

completely into C++.

---

## 7. Multi-Symbol Sharding

Scale matching engine using:
- symbol partitioning
- independent matching cores
- parallel execution

---

## 8. Persistence Layer

Add:
- write-ahead logging
- event sourcing
- recovery mechanisms

---

# Resume Value

This project demonstrates:

- Low-latency systems engineering
- Exchange infrastructure design
- Native C++ performance optimization
- Python/C++ interoperability
- Benchmarking methodology
- Systems architecture evolution
- Quantitative performance analysis

---

# Final Thoughts

The most valuable aspect of this project was not just building a matching engine.

It was:
- measuring bottlenecks
- iterating on architecture
- validating assumptions
- benchmarking every stage
- understanding where latency actually comes from

The project evolved from a simple Python exchange simulator into a genuinely low-latency native matching engine capable of sub-microsecond median latency.

This mirrors the iterative optimization process used in real trading systems and exchange infrastructure engineering.
