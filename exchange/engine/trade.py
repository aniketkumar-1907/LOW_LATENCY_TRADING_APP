class Trade:

    def __init__(self):

        self.buy_order_id = None
        self.sell_order_id = None
        self.price = None
        self.quantity = None
        self.timestamp = None

    def reset(
        self,
        buy_order_id,
        sell_order_id,
        price,
        quantity,
        timestamp
    ):

        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp