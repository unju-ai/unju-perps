"""
Example agent tool integration for unju-agent
"""

from typing import Literal, Optional
from unju_perps import PerpTrader
from unju_perps.types import RiskLimits


# Initialize trader (in real usage, this would be a singleton or per-agent instance)
_trader = None


def get_trader() -> PerpTrader:
    """Get or create PerpTrader instance"""
    global _trader
    if _trader is None:
        _trader = PerpTrader(
            testnet=True,
            risk_limits=RiskLimits(
                max_position_size_usd=5000.0,
                max_leverage=10.0,
                allowed_symbols=["BTC", "ETH", "SOL", "ARB", "OP"],
            )
        )
    return _trader


def trade_perp(
    symbol: str,
    action: Literal["long", "short", "close"],
    size_usd: float,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None,
) -> dict:
    """
    Execute perpetual futures trade on Hyperliquid.
    
    Tool for AI agents to trade perpetual futures with built-in risk management.
    
    Args:
        symbol: Asset symbol (e.g., "BTC", "ETH", "SOL")
        action: Trade action - "long" to buy, "short" to sell, "close" to close position
        size_usd: Position size in USD (ignored for close action)
        stop_loss_pct: Optional stop loss percentage (e.g., 2.0 for 2%)
        take_profit_pct: Optional take profit percentage (e.g., 5.0 for 5%)
    
    Returns:
        Dictionary with order details:
        - status: "success" or "error"
        - order_id: Order ID
        - symbol: Asset symbol
        - side: Position side
        - entry_price: Execution price
        - size: Position size
        - pnl: Realized PnL (for close actions)
        - fees: Trading fees paid
        - message: Human-readable status message
    
    Examples:
        >>> trade_perp("BTC", "long", 100.0, stop_loss_pct=2.0)
        >>> trade_perp("ETH", "short", 50.0, take_profit_pct=3.0)
        >>> trade_perp("SOL", "close", 0)
    """
    trader = get_trader()
    
    try:
        if action == "close":
            order = trader.close_position(symbol)
            position = None  # Position closed
        else:
            order = trader.market_order(
                symbol=symbol,
                side=action,
                size_usd=size_usd,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
            )
            position = trader.get_position(symbol)
        
        return {
            "status": "success",
            "order_id": order.id,
            "symbol": symbol,
            "side": order.side.value,
            "entry_price": order.average_price,
            "size": order.filled_size,
            "fees": order.fees,
            "pnl": position.unrealized_pnl if position else 0.0,
            "liquidation_price": position.liquidation_price if position else None,
            "message": f"{'Opened' if action != 'close' else 'Closed'} {symbol} {action} position at ${order.average_price:.2f}",
        }
    
    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol,
            "action": action,
            "message": f"Trade failed: {str(e)}",
        }


def get_perp_positions() -> dict:
    """
    Get all open perpetual futures positions.
    
    Returns:
        Dictionary with:
        - positions: List of open positions with details
        - total_pnl: Total unrealized PnL across all positions
        - total_margin: Total margin used
    """
    trader = get_trader()
    
    try:
        positions = trader.get_all_positions()
        
        position_list = []
        total_pnl = 0.0
        total_margin = 0.0
        
        for pos in positions:
            position_list.append({
                "symbol": pos.symbol,
                "side": pos.side.value,
                "size": pos.size,
                "entry_price": pos.entry_price,
                "mark_price": pos.mark_price,
                "leverage": pos.leverage,
                "unrealized_pnl": pos.unrealized_pnl,
                "liquidation_price": pos.liquidation_price,
            })
            total_pnl += pos.unrealized_pnl
            total_margin += pos.margin
        
        return {
            "status": "success",
            "positions": position_list,
            "total_pnl": total_pnl,
            "total_margin": total_margin,
            "message": f"{len(positions)} open position(s), total PnL: ${total_pnl:.2f}",
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch positions: {str(e)}",
        }


def get_perp_market(symbol: str) -> dict:
    """
    Get current market data for a perpetual futures symbol.
    
    Args:
        symbol: Asset symbol (e.g., "BTC", "ETH")
    
    Returns:
        Dictionary with current market data:
        - mark_price: Current mark price
        - index_price: Index price
        - funding_rate: Current funding rate
        - volume_24h: 24h trading volume
        - change_24h: 24h price change percentage
    """
    trader = get_trader()
    
    try:
        market = trader.get_market_data(symbol)
        
        return {
            "status": "success",
            "symbol": symbol,
            "mark_price": market.mark_price,
            "index_price": market.index_price,
            "funding_rate": market.funding_rate * 100,  # As percentage
            "volume_24h": market.volume_24h,
            "change_24h": market.change_24h,
            "message": f"{symbol}: ${market.mark_price:.2f} ({market.change_24h:+.2f}% 24h)",
        }
    
    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol,
            "message": f"Failed to fetch market data: {str(e)}",
        }
