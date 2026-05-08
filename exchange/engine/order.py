from dataclasses import dataclass
import time
import uuid


@dataclass
class Order:
    symbol: str
    side: str
    order_type: str
    quantity: int
    price: float | None
    order_id: str = ""
    timestamp: int = 0

    def __post_init__(self):

        if not self.order_id:
            self.order_id = str(uuid.uuid4())

        if not self.timestamp:
            self.timestamp = int(time.time() * 1_000_000)