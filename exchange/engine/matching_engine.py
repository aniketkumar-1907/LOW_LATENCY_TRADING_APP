import time

from exchange.engine.order_book import OrderBook
from exchange.engine.order_registry import OrderRegistry
from exchange.engine.enums import Side
from exchange.engine.object_pool import ObjectPool
from exchange.engine.trade import Trade


class MatchingEngine:

    def __init__(self):

        # Preallocated trade object pool
        self.trade_pool = ObjectPool(
            Trade,
            10000
        )

        # symbol -> order book
        self.order_books = {}

        self.order_registry = OrderRegistry()

    # =========================
    # Get/Create Order Book
    # =========================

    def get_order_book(self, symbol):

        if symbol not in self.order_books:

            self.order_books[symbol] = OrderBook()

        return self.order_books[symbol]

    # =========================
    # Main Entry Point
    # =========================

    def process_order(self, order):

        order_book = self.get_order_book(
            order.symbol
        )

        if order.side == Side.BUY.value:

            return self.match_buy_order(
                order_book,
                order
            )

        elif order.side == Side.SELL.value:

            return self.match_sell_order(
                order_book,
                order
            )

        return []

    # =========================
    # Cancel Order
    # =========================

    def cancel_order(self, order_id):

        order = self.order_registry.get(
            order_id
        )

        if not order:
            return False

        order_book = self.get_order_book(
            order.symbol
        )

        removed = order_book.remove_order(
            order
        )

        if removed:

            self.order_registry.remove(
                order_id
            )

        return removed

    # =========================
    # Match BUY Order
    # =========================

    def match_buy_order(
        self,
        order_book,
        buy_order
    ):

        trades = []

        while buy_order.quantity > 0:

            best_ask = order_book.get_best_ask()

            if best_ask is None:
                break

            # LIMIT order price check
            if (
                buy_order.order_type == "LIMIT"
                and buy_order.price < best_ask
            ):
                break

            ask_queue = order_book.asks[
                best_ask
            ]

            sell_order = ask_queue[0]

            traded_quantity = min(
                buy_order.quantity,
                sell_order.quantity
            )

            # Reuse pooled trade object
            trade = self.trade_pool.acquire()

            trade.reset(
                buy_order_id=buy_order.order_id,
                sell_order_id=sell_order.order_id,
                price=best_ask,
                quantity=traded_quantity,
                timestamp=int(
                    time.time() * 1_000_000
                )
            )

            trades.append(trade)

            # Update quantities
            buy_order.quantity -= traded_quantity
            sell_order.quantity -= traded_quantity

            # Remove completed SELL order
            if sell_order.quantity == 0:

                ask_queue.popleft()

                self.order_registry.remove(
                    sell_order.order_id
                )

            # Remove empty price level
            if len(ask_queue) == 0:

                del order_book.asks[best_ask]

        # Add remaining LIMIT order to book
        if (
            buy_order.quantity > 0
            and buy_order.order_type == "LIMIT"
        ):

            order_book.add_order(buy_order)

            self.order_registry.add(
                buy_order
            )

        return trades

    # =========================
    # Match SELL Order
    # =========================

    def match_sell_order(
        self,
        order_book,
        sell_order
    ):

        trades = []

        while sell_order.quantity > 0:

            best_bid = order_book.get_best_bid()

            if best_bid is None:
                break

            # LIMIT order price check
            if (
                sell_order.order_type == "LIMIT"
                and sell_order.price > best_bid
            ):
                break

            bid_queue = order_book.bids[
                best_bid
            ]

            buy_order = bid_queue[0]

            traded_quantity = min(
                sell_order.quantity,
                buy_order.quantity
            )

            # Reuse pooled trade object
            trade = self.trade_pool.acquire()

            trade.reset(
                buy_order_id=buy_order.order_id,
                sell_order_id=sell_order.order_id,
                price=best_bid,
                quantity=traded_quantity,
                timestamp=int(
                    time.time() * 1_000_000
                )
            )

            trades.append(trade)

            # Update quantities
            sell_order.quantity -= traded_quantity
            buy_order.quantity -= traded_quantity

            # Remove completed BUY order
            if buy_order.quantity == 0:

                bid_queue.popleft()

                self.order_registry.remove(
                    buy_order.order_id
                )

            # Remove empty price level
            if len(bid_queue) == 0:

                del order_book.bids[best_bid]

        # Add remaining LIMIT order to book
        if (
            sell_order.quantity > 0
            and sell_order.order_type == "LIMIT"
        ):

            order_book.add_order(sell_order)

            self.order_registry.add(
                sell_order
            )

        return trades