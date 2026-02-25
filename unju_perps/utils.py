"""Utility functions"""

from typing import Optional
import os


def get_private_key_from_env(var_name: str = "HYPERLIQUID_PRIVATE_KEY") -> Optional[str]:
    """
    Load private key from environment variable.
    
    Args:
        var_name: Environment variable name
    
    Returns:
        Private key string or None if not set
    """
    key = os.getenv(var_name)
    if key and not key.startswith("0x"):
        key = f"0x{key}"
    return key


def calculate_position_size(
    notional_usd: float,
    entry_price: float,
    leverage: float = 1.0,
) -> float:
    """
    Calculate position size in contracts from USD notional.
    
    Args:
        notional_usd: Position size in USD
        entry_price: Entry price
        leverage: Leverage multiplier
    
    Returns:
        Position size in contracts
    """
    return (notional_usd * leverage) / entry_price


def calculate_liquidation_price(
    entry_price: float,
    leverage: float,
    side: str,
    maintenance_margin: float = 0.005,  # 0.5% default
) -> float:
    """
    Estimate liquidation price for a position.
    
    Args:
        entry_price: Entry price
        leverage: Leverage multiplier
        side: "long" or "short"
        maintenance_margin: Maintenance margin rate
    
    Returns:
        Estimated liquidation price
    """
    if side.lower() == "long":
        # Long liquidation: price drops
        return entry_price * (1 - (1 / leverage) + maintenance_margin)
    else:
        # Short liquidation: price rises
        return entry_price * (1 + (1 / leverage) - maintenance_margin)


def format_symbol(symbol: str) -> str:
    """
    Normalize symbol format.
    
    Args:
        symbol: Raw symbol (e.g., "BTC", "btc", "BTCUSD")
    
    Returns:
        Normalized symbol
    """
    symbol = symbol.upper().replace("USD", "").replace("USDT", "").replace("-", "")
    return symbol
