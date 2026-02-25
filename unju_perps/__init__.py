"""
unju-perps: MCP Server for AI agents to trade perpetual futures on Hyperliquid
"""

from unju_perps.client import PerpTrader
from unju_perps.wallet import WalletManager
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
    "WalletManager",
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
