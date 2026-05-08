import json
import time
import uuid
from dataclasses import dataclass, asdict
from enum import Enum


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


@dataclass
class Order:
    symbol: str
    side: str
    order_type: str
    quantity: int
    price: float | None = None
    order_id: str = ""
    timestamp: int = 0

    def __post_init__(self):
        if not self.order_id:
            self.order_id = str(uuid.uuid4())

        if not self.timestamp:
            self.timestamp = int(time.time() * 1000)

    def to_json(self):
        return json.dumps(asdict(self))