from cpp_matching_engine import (
    MatchingEngine,
    Order
)

engine = MatchingEngine()

buy = Order()
buy.symbol = "AAPL"
buy.side = "BUY"
buy.order_type = "LIMIT"
buy.quantity = 100
buy.price = 150.0
buy.order_id = "BUY1"
buy.timestamp = 1

engine.process_order(buy)

sell = Order()
sell.symbol = "AAPL"
sell.side = "SELL"
sell.order_type = "MARKET"
sell.quantity = 50
sell.price = 0
sell.order_id = "SELL1"
sell.timestamp = 2

trades = engine.process_order(sell)

for trade in trades:

    print(
        trade.buy_order_id,
        trade.sell_order_id,
        trade.price,
        trade.quantity
    )