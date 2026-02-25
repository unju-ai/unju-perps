"""
Test script to demonstrate unju-perps MCP server capabilities.

This script shows how the server works with mock data before
connecting to real Hyperliquid/Magic APIs.
"""
import json
import asyncio
from unju_perps import PerpTrader
from unju_perps.types import OrderSide


async def demo():
    """Demo the trading client with mock data."""
    
    print("🚀 unju-perps Demo - Phase 1 (Mock Data)\n")
    print("=" * 60)
    
    # Initialize trader with mock key
    trader = PerpTrader(
        private_key="0x" + "1" * 64,  # Mock key
        testnet=True
    )
    
    print(f"\n💰 Initial Balance")
    print("-" * 60)
    balance = trader.get_balance()
    print(f"Total: ${balance.total:,.2f}")
    print(f"Available: ${balance.available:,.2f}")
    
    # Place a market order
    print(f"\n📈 Placing Market Order: Long BTC $1000")
    print("-" * 60)
    order = trader.market_order(
        symbol="BTC",
        side=OrderSide.LONG,
        size_usd=1000.0
    )
    print(f"Order ID: {order.id}")
    print(f"Filled: {order.filled_size:.6f} BTC @ ${order.average_price:,.2f}")
    print(f"Fees: ${order.fees:.2f}")
    
    # Check position
    print(f"\n📊 Position Status")
    print("-" * 60)
    position = trader.get_position("BTC")
    if position:
        print(f"Symbol: {position.symbol}")
        print(f"Side: {position.side.value.upper()}")
        print(f"Size: {position.size:.6f}")
        print(f"Entry: ${position.entry_price:,.2f}")
        print(f"Current: ${position.mark_price:,.2f}")
        print(f"Liquidation: ${position.liquidation_price:,.2f}")
        print(f"Leverage: {position.leverage}x")
        print(f"P&L: ${position.unrealized_pnl:+,.2f}")
    
    # Get all positions
    print(f"\n📋 All Positions")
    print("-" * 60)
    positions = trader.get_all_positions()
    for pos in positions:
        pnl_pct = (pos.unrealized_pnl / (pos.size * pos.entry_price)) * 100
        print(f"{pos.symbol:6s} {pos.side.value.upper():5s} | "
              f"Entry: ${pos.entry_price:,.2f} | "
              f"P&L: ${pos.unrealized_pnl:+.2f} ({pnl_pct:+.2f}%)")
    
    # Place another order
    print(f"\n📉 Placing Another Order: Long ETH $500")
    print("-" * 60)
    order2 = trader.market_order(
        symbol="ETH",
        side=OrderSide.LONG,
        size_usd=500.0
    )
    print(f"Filled: {order2.filled_size:.6f} ETH @ ${order2.average_price:,.2f}")
    
    # Final balance
    print(f"\n💰 Final Balance")
    print("-" * 60)
    balance = trader.get_balance()
    print(f"Total: ${balance.total:,.2f}")
    print(f"Available: ${balance.available:,.2f}")
    print(f"Margin Used: ${balance.margin_used:,.2f}")
    print(f"Unrealized P&L: ${balance.unrealized_pnl:+,.2f}")
    
    # Market data
    print(f"\n📊 Market Data (BTC)")
    print("-" * 60)
    market = trader.get_market_data("BTC")
    print(f"Mark Price: ${market.mark_price:,.2f}")
    print(f"Index Price: ${market.index_price:,.2f}")
    print(f"Funding Rate: {market.funding_rate * 100:.4f}%")
    print(f"24h Volume: ${market.volume_24h:,.0f}")
    print(f"24h Change: {market.change_24h:+.2f}%")
    
    # Close position
    print(f"\n❌ Closing BTC Position")
    print("-" * 60)
    close_order = trader.close_position("BTC")
    print(f"Closed at: ${close_order.average_price:,.2f}")
    print(f"Fees: ${close_order.fees:.2f}")
    
    # Final positions
    print(f"\n📋 Remaining Positions")
    print("-" * 60)
    positions = trader.get_all_positions()
    if positions:
        for pos in positions:
            pnl_pct = (pos.unrealized_pnl / (pos.size * pos.entry_price)) * 100
            print(f"{pos.symbol:6s} {pos.side.value.upper():5s} | "
                  f"P&L: ${pos.unrealized_pnl:+.2f} ({pnl_pct:+.2f}%)")
    else:
        print("No open positions")
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("\nNext Steps:")
    print("1. Run MCP server: python -m unju_perps --stdio")
    print("2. Configure Claude Desktop (see README.md)")
    print("3. Test with interactive UIs")
    print("\nPhase 2 will add:")
    print("- Real Hyperliquid SDK integration")
    print("- Real Magic wallet API")
    print("- Real unju credits system")


if __name__ == "__main__":
    asyncio.run(demo())
