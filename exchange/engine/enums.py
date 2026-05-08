from enum import Enum


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class MessageType(Enum):
    NEW_ORDER = "NEW_ORDER"
    CANCEL_ORDER = "CANCEL_ORDER"