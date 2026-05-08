import heapq
from collections import defaultdict, deque


class OrderBook:

    def __init__(self):

        # price -> queue of orders
        self.bids = defaultdict(deque)
        self.asks = defaultdict(deque)

        # heaps for best prices
        self.bid_heap = []
        self.ask_heap = []

    # =========================
    # Add Order
    # =========================

    def add_order(self, order):

        price = order.price

        # BUY SIDE
        if order.side == "BUY":

            # New price level
            if price not in self.bids:

                heapq.heappush(
                    self.bid_heap,
                    -price
                )

            self.bids[price].append(order)

        # SELL SIDE
        else:

            if price not in self.asks:

                heapq.heappush(
                    self.ask_heap,
                    price
                )

            self.asks[price].append(order)

    # =========================
    # Best Bid
    # =========================

    def get_best_bid(self):

        while self.bid_heap:

            best_price = -self.bid_heap[0]

            # Lazy cleanup
            if (
                best_price in self.bids
                and len(self.bids[best_price]) > 0
            ):

                return best_price

            heapq.heappop(self.bid_heap)

        return None

    # =========================
    # Best Ask
    # =========================

    def get_best_ask(self):

        while self.ask_heap:

            best_price = self.ask_heap[0]

            if (
                best_price in self.asks
                and len(self.asks[best_price]) > 0
            ):

                return best_price

            heapq.heappop(self.ask_heap)

        return None