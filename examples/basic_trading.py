"""
Basic trading example with unju-perps
"""

from unju_perps import PerpTrader
from unju_perps.types import RiskLimits

# Initialize trader with testnet and risk limits
trader = PerpTrader(
    private_key="0x...",  # Your private key
    testnet=True,
    risk_limits=RiskLimits(
        max_position_size_usd=1000.0,
        max_leverage=5.0,
        allowed_symbols=["BTC", "ETH", "SOL"],
    )
)

# Check account balance
balance = trader.get_balance()
print(f"Balance: ${balance.available:.2f} available")

# Get market data
market = trader.get_market_data("BTC")
print(f"BTC Mark Price: ${market.mark_price:.2f}")
print(f"Funding Rate: {market.funding_rate * 100:.4f}%")

# Place a market order (long BTC)
order = trader.market_order(
    symbol="BTC",
    side="long",
    size_usd=100.0,
    slippage_bps=50,  # 0.5% max slippage
    stop_loss_pct=2.0,  # 2% stop loss
)
print(f"Order filled at ${order.average_price:.2f}")

# Check position
position = trader.get_position("BTC")
if position:
    print(f"Position: {position.side} {position.size} @ ${position.entry_price:.2f}")
    print(f"Unrealized PnL: ${position.unrealized_pnl:.2f}")
    print(f"Liquidation Price: ${position.liquidation_price:.2f}")

# Close position
close_order = trader.close_position("BTC")
print(f"Position closed at ${close_order.average_price:.2f}")
