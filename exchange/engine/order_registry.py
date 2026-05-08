class OrderRegistry:

    def __init__(self):
        self.orders = {}

    def add(self, order):
        self.orders[order.order_id] = order

    def get(self, order_id):
        return self.orders.get(order_id)

    def remove(self, order_id):

        if order_id in self.orders:
            del self.orders[order_id]