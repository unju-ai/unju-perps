"""
unju-perps: Agent-friendly wrapper over Hyperliquid SDK
"""

from unju_perps.client import PerpTrader
from unju_perps.types import Order, Position, Market, OrderSide, OrderType
from unju_perps.exceptions import (
    UnjuPerpsError,
    InsufficientBalanceError,
    InvalidSymbolError,
    OrderRejectedError,
    RiskLimitExceededError,
)

__version__ = "0.1.0"

__all__ = [
    "PerpTrader",
    "Order",
    "Position",
    "Market",
    "OrderSide",
    "OrderType",
    "UnjuPerpsError",
    "InsufficientBalanceError",
    "InvalidSymbolError",
    "OrderRejectedError",
    "RiskLimitExceededError",
]
