"""Type definitions for unju-perps"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    """Order side"""
    LONG = "long"
    SHORT = "short"


class OrderType(str, Enum):
    """Order type"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order(BaseModel):
    """Order representation"""
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    size: float
    price: Optional[float] = None
    filled_size: float = 0.0
    average_price: Optional[float] = None
    status: OrderStatus
    timestamp: datetime
    fees: float = 0.0


class Position(BaseModel):
    """Position representation"""
    symbol: str
    side: OrderSide
    size: float
    entry_price: float
    mark_price: float
    liquidation_price: Optional[float] = None
    leverage: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    margin: float
    timestamp: datetime


class Market(BaseModel):
    """Market data"""
    symbol: str
    mark_price: float
    index_price: float
    funding_rate: float
    open_interest: float
    volume_24h: float
    high_24h: float
    low_24h: float
    change_24h: float
    timestamp: datetime


class Balance(BaseModel):
    """Account balance"""
    total: float
    available: float
    margin_used: float
    unrealized_pnl: float
    timestamp: datetime


class RiskLimits(BaseModel):
    """Risk management limits"""
    max_position_size_usd: float = Field(default=10000.0, ge=0)
    max_leverage: float = Field(default=10.0, ge=1.0, le=50.0)
    max_daily_loss_usd: float = Field(default=1000.0, ge=0)
    max_open_orders: int = Field(default=10, ge=1)
    allowed_symbols: Optional[list[str]] = None
