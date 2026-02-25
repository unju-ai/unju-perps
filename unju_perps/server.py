#!/usr/bin/env python3
"""
unju-perps MCP Server

MCP server for trading perpetual futures on Hyperliquid with interactive UIs.
Uses Magic server wallets and unju credits system.
"""
import os
import sys
import json
import asyncio
from typing import Optional, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp import types

from .client import PerpTrader
from .wallet import WalletManager
from .types import OrderSide
from .exceptions import (
    InsufficientBalanceError,
    InvalidSymbolError,
    RiskLimitExceededError,
)

# UI Resource URIs
VIEW_DASHBOARD = "ui://perps/dashboard"
VIEW_POSITION = "ui://perps/position"
VIEW_RISK = "ui://perps/risk-config"
VIEW_WALLET = "ui://perps/wallet-setup"

# Configuration
TESTNET = os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "3001"))

# Initialize FastMCP
mcp = FastMCP("unju-perps", stateless_http=True)

# Global wallet manager (in production, this would be per-user)
wallet_manager = WalletManager()


def get_trader(user_id: Optional[str] = None) -> PerpTrader:
    """
    Get or create trader instance for user.
    
    In production, user_id comes from MCP host authentication.
    For now, we use a default user or HYPERLIQUID_PRIVATE_KEY env var.
    """
    # Try to get wallet from Magic or env var
    private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
    
    if not private_key:
        # User needs to create/connect wallet first
        raise Exception("No wallet configured. Please run wallet_setup first.")
    
    return PerpTrader(
        private_key=private_key,
        testnet=TESTNET
    )


# ============================================================================
# WALLET MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(meta={"ui": {"resourceUri": VIEW_WALLET}})
def wallet_setup(
    action: str = "info",
    email: Optional[str] = None
) -> list[types.TextContent]:
    """
    Set up or manage your trading wallet.
    
    Args:
        action: Action to perform (info, create, fund)
        email: Email for Magic wallet creation (required for create)
    
    Returns wallet status and funding information.
    """
    if action == "create":
        if not email:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Email required for wallet creation",
                    "action": "create",
                    "cost": "1 unju-credit + 10 credits/year rent"
                })
            )]
        
        # Create Magic wallet and charge 1 credit
        result = wallet_manager.create_wallet(email)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "action": "created",
                "address": result["address"],
                "email": email,
                "credits_charged": 1,
                "annual_rent": 10,
                "next_rent_due": result["next_rent_due"],
                "funded": False,
                "message": "✨ Wallet created! Please fund it to start trading."
            })
        )]
    
    elif action == "fund":
        # Get funding instructions
        trader = get_trader()
        address = trader.address
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "action": "fund",
                "address": address,
                "network": "Arbitrum" if not TESTNET else "Arbitrum Testnet",
                "min_amount": "10 USDC",
                "instructions": [
                    "1. Get USDC on Arbitrum",
                    "2. Send to your wallet address",
                    "3. Wait for confirmation",
                    "4. Start trading!"
                ],
                "testnet_faucet": "https://faucet.hyperliquid-testnet.xyz" if TESTNET else None
            })
        )]
    
    else:  # info
        try:
            trader = get_trader()
            balance = trader.get_balance()
            wallet_info = wallet_manager.get_wallet_info(trader.address)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "action": "info",
                    "address": trader.address,
                    "balance": balance.total,
                    "available": balance.available,
                    "margin_used": balance.margin_used,
                    "credits_remaining": wallet_info.get("credits_remaining", 0),
                    "rent_due": wallet_info.get("next_rent_due"),
                    "active": wallet_info.get("active", True),
                    "message": f"💰 Balance: ${balance.total:.2f} | Rent due: {wallet_info.get('next_rent_due')}"
                })
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "action": "info",
                    "error": str(e),
                    "message": "⚠️ No wallet configured. Run wallet_setup with action=create"
                })
            )]


# ============================================================================
# TRADING TOOLS
# ============================================================================

@mcp.tool()
def market_order(
    symbol: str,
    side: str,
    size_usd: float,
    slippage_bps: int = 50,
    stop_loss_pct: Optional[float] = None,
    take_profit_pct: Optional[float] = None
) -> list[types.TextContent]:
    """
    Execute a market order.
    
    Args:
        symbol: Asset symbol (BTC, ETH, SOL, etc.)
        side: Order side (long or short)
        size_usd: Position size in USD
        slippage_bps: Max slippage in basis points (50 = 0.5%)
        stop_loss_pct: Optional stop loss percentage from entry
        take_profit_pct: Optional take profit percentage from entry
    """
    try:
        trader = get_trader()
        
        order = trader.market_order(
            symbol=symbol,
            side=OrderSide(side.lower()),
            size_usd=size_usd,
            slippage_bps=slippage_bps,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "order_id": order.id,
                "symbol": order.symbol,
                "side": order.side.value,
                "size": order.size,
                "entry_price": order.average_price,
                "fees_usd": order.fees,
                "timestamp": order.timestamp.isoformat(),
                "message": f"✅ {order.side.value.title()} {order.symbol}: ${size_usd} @ ${order.average_price:.2f}"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Order failed: {str(e)}"
            })
        )]


@mcp.tool(meta={"ui": {"resourceUri": VIEW_POSITION}})
def get_position(symbol: str) -> list[types.TextContent]:
    """
    Get detailed position information with interactive chart.
    
    Args:
        symbol: Asset symbol
    """
    try:
        trader = get_trader()
        position = trader.get_position(symbol)
        
        if not position:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "Position not found",
                    "symbol": symbol,
                    "message": f"📊 No open position for {symbol}"
                })
            )]
        
        # Get price history for chart
        price_history = trader.get_price_history(symbol, hours=4)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "symbol": position.symbol,
                "side": position.side.value,
                "size": position.size,
                "entry_price": position.entry_price,
                "mark_price": position.mark_price,
                "liquidation_price": position.liquidation_price,
                "leverage": position.leverage,
                "unrealized_pnl": position.unrealized_pnl,
                "unrealized_pnl_pct": (position.unrealized_pnl / (position.size * position.entry_price) * 100),
                "margin": position.margin,
                "price_history": price_history,
                "message": f"📊 {symbol} {position.side.value.title()}: ${position.unrealized_pnl:+.2f}"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Failed to get position: {str(e)}"
            })
        )]


@mcp.tool(meta={"ui": {"resourceUri": VIEW_DASHBOARD}})
def get_dashboard(refresh_interval: int = 5) -> list[types.TextContent]:
    """
    Get interactive portfolio dashboard.
    
    Args:
        refresh_interval: Auto-refresh interval in seconds (0 = disabled)
    """
    try:
        trader = get_trader()
        
        balance = trader.get_balance()
        positions = trader.get_all_positions()
        balance_history = trader.get_balance_history(days=7)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "balance": {
                    "total": balance.total,
                    "available": balance.available,
                    "margin_used": balance.margin_used,
                    "unrealized_pnl": balance.unrealized_pnl
                },
                "positions": [
                    {
                        "symbol": p.symbol,
                        "side": p.side.value,
                        "size": p.size,
                        "entry_price": p.entry_price,
                        "mark_price": p.mark_price,
                        "unrealized_pnl": p.unrealized_pnl,
                        "unrealized_pnl_pct": (p.unrealized_pnl / (p.size * p.entry_price) * 100)
                    }
                    for p in positions
                ],
                "balance_history": balance_history,
                "refresh_interval": refresh_interval,
                "message": f"💰 Portfolio: ${balance.total:.2f} | P&L: ${balance.unrealized_pnl:+.2f}"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Failed to get dashboard: {str(e)}"
            })
        )]


@mcp.tool()
def close_position(
    symbol: str,
    slippage_bps: int = 50
) -> list[types.TextContent]:
    """
    Close an open position.
    
    Args:
        symbol: Asset symbol
        slippage_bps: Max slippage in basis points
    """
    try:
        trader = get_trader()
        order = trader.close_position(symbol, slippage_bps=slippage_bps)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "order_id": order.id,
                "symbol": order.symbol,
                "size": order.size,
                "exit_price": order.average_price,
                "realized_pnl": order.fees,  # TODO: Calculate actual PnL
                "fees_usd": order.fees,
                "message": f"✅ Closed {symbol}: ${order.average_price:.2f}"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Failed to close position: {str(e)}"
            })
        )]


@mcp.tool()
def get_balance() -> list[types.TextContent]:
    """Get account balance and margin info."""
    try:
        trader = get_trader()
        balance = trader.get_balance()
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "total": balance.total,
                "available": balance.available,
                "margin_used": balance.margin_used,
                "unrealized_pnl": balance.unrealized_pnl,
                "buying_power": balance.available * 10,  # Assuming 10x leverage
                "message": f"💵 Balance: ${balance.total:.2f} | Available: ${balance.available:.2f}"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Failed to get balance: {str(e)}"
            })
        )]


@mcp.tool()
def get_market_data(symbol: str) -> list[types.TextContent]:
    """
    Get current market data.
    
    Args:
        symbol: Asset symbol
    """
    try:
        trader = get_trader()
        market = trader.get_market_data(symbol)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "symbol": market.symbol,
                "mark_price": market.mark_price,
                "index_price": market.index_price,
                "funding_rate": market.funding_rate,
                "funding_rate_annual": market.funding_rate * 365 * 3 * 100,  # Approximate
                "open_interest": market.open_interest,
                "volume_24h": market.volume_24h,
                "high_24h": market.high_24h,
                "low_24h": market.low_24h,
                "change_24h": market.change_24h,
                "message": f"📊 {symbol}: ${market.mark_price:.2f} | Funding: {market.funding_rate*100:.4f}%"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Failed to get market data: {str(e)}"
            })
        )]


@mcp.tool(meta={"ui": {"resourceUri": VIEW_RISK}})
def configure_risk(
    max_position_size_usd: Optional[float] = None,
    max_leverage: Optional[float] = None,
    max_daily_loss_usd: Optional[float] = None,
    allowed_symbols: Optional[list[str]] = None
) -> list[types.TextContent]:
    """
    Configure risk management limits.
    
    Args:
        max_position_size_usd: Max position size in USD
        max_leverage: Max leverage allowed (1-50)
        max_daily_loss_usd: Max daily loss before circuit breaker
        allowed_symbols: Whitelist of allowed symbols (empty = all)
    """
    try:
        trader = get_trader()
        
        if max_position_size_usd:
            trader.risk_manager.limits.max_position_size_usd = max_position_size_usd
        if max_leverage:
            trader.risk_manager.limits.max_leverage = max_leverage
        if max_daily_loss_usd:
            trader.risk_manager.limits.max_daily_loss_usd = max_daily_loss_usd
        if allowed_symbols is not None:
            trader.risk_manager.limits.allowed_symbols = allowed_symbols
        
        limits = trader.risk_manager.limits
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "max_position_size_usd": limits.max_position_size_usd,
                "max_leverage": limits.max_leverage,
                "max_daily_loss_usd": limits.max_daily_loss_usd,
                "allowed_symbols": limits.allowed_symbols or [],
                "current_daily_loss": trader.risk_manager.daily_pnl,
                "circuit_breaker_active": trader.risk_manager.daily_pnl < -limits.max_daily_loss_usd,
                "message": f"🛡️ Risk limits updated: ${limits.max_position_size_usd:.0f} max, {limits.max_leverage}x leverage"
            })
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "message": f"❌ Failed to configure risk: {str(e)}"
            })
        )]


# ============================================================================
# UI RESOURCES
# ============================================================================

@mcp.resource(
    VIEW_WALLET,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com"]}}}
)
def wallet_view() -> str:
    """Wallet setup UI."""
    try:
        with open(os.path.join(os.path.dirname(__file__), "views", "wallet.html")) as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Wallet Setup View</h1><p>Coming soon...</p></body></html>"


@mcp.resource(
    VIEW_DASHBOARD,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com", "https://cdn.plot.ly"]}}}
)
def dashboard_view() -> str:
    """Interactive dashboard UI."""
    try:
        with open(os.path.join(os.path.dirname(__file__), "views", "dashboard.html")) as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Dashboard View</h1><p>Coming soon...</p></body></html>"


@mcp.resource(
    VIEW_POSITION,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com", "https://cdn.plot.ly"]}}}
)
def position_view() -> str:
    """Position detail UI."""
    try:
        with open(os.path.join(os.path.dirname(__file__), "views", "position.html")) as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Position View</h1><p>Coming soon...</p></body></html>"


@mcp.resource(
    VIEW_RISK,
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com"]}}}
)
def risk_view() -> str:
    """Risk configuration UI."""
    try:
        with open(os.path.join(os.path.dirname(__file__), "views", "risk.html")) as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Risk Config View</h1><p>Coming soon...</p></body></html>"


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

def main():
    """Run the MCP server."""
    if "--stdio" in sys.argv:
        # Claude Desktop / stdio mode
        mcp.run(transport="stdio")
    else:
        # HTTP mode for testing
        import uvicorn
        from starlette.middleware.cors import CORSMiddleware
        
        app = mcp.streamable_http_app()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        print(f"unju-perps MCP Server listening on http://{HOST}:{PORT}/mcp", file=sys.stderr)
        print(f"Testnet mode: {TESTNET}", file=sys.stderr)
        uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
