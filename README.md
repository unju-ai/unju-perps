# unju-perps

**Agent-friendly wrapper over Hyperliquid SDK for perpetual futures trading**

A thin, opinionated layer that makes it dead simple for AI agents to trade perps on Hyperliquid.

## Features

- 🤖 **Agent-First API** — designed for LLM tool calling
- 🔐 **Secure by default** — wallet management, signing, nonce handling
- 📊 **Rich market data** — positions, orders, funding, liquidations
- ⚡ **Fast execution** — minimal overhead over raw SDK
- 🛡️ **Risk controls** — position limits, max leverage, circuit breakers

## Quick Start

```python
from unju_perps import PerpTrader

# Initialize with private key or agent vault
trader = PerpTrader(
    private_key="0x...",
    testnet=True
)

# Place a market order
order = trader.market_order(
    symbol="BTC",
    side="long",
    size_usd=100.0,
    slippage_bps=50  # 0.5% max slippage
)

# Check position
position = trader.get_position("BTC")
print(f"PnL: ${position.unrealized_pnl}")

# Close position
trader.close_position("BTC")
```

## Installation

```bash
pip install unju-perps
```

Or from source:
```bash
git clone https://github.com/unju-ai/unju-perps.git
cd unju-perps
pip install -e .
```

## Architecture

```
unju-perps/
├── unju_perps/
│   ├── __init__.py
│   ├── client.py          # Main PerpTrader class
│   ├── types.py           # Order, Position, Market types
│   ├── risk.py            # Risk management & limits
│   ├── utils.py           # Helpers (vault integration, etc.)
│   └── exceptions.py      # Custom exceptions
├── tests/
└── examples/
```

## Agent Integration

Designed to work seamlessly with unju-agent tool calling:

```python
@tool
def trade_perp(
    symbol: str,
    action: Literal["long", "short", "close"],
    size_usd: float,
    stop_loss_pct: Optional[float] = None
) -> dict:
    """
    Execute perpetual futures trade on Hyperliquid.
    
    Args:
        symbol: Asset symbol (e.g., "BTC", "ETH", "SOL")
        action: Trade action (long/short/close)
        size_usd: Position size in USD
        stop_loss_pct: Optional stop loss percentage
    
    Returns:
        Order confirmation with entry price, fees, position details
    """
    trader = get_trader()  # Get authenticated instance
    
    if action == "close":
        return trader.close_position(symbol)
    
    return trader.market_order(
        symbol=symbol,
        side=action,
        size_usd=size_usd,
        stop_loss_pct=stop_loss_pct
    )
```

## Security

- Private keys never logged or transmitted
- Optional integration with unju vault system
- Configurable risk limits per agent/account
- Testnet mode for safe experimentation

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy unju_perps/
```

## Roadmap

- [ ] Basic market orders (long/short/close)
- [ ] Limit orders & advanced order types
- [ ] Stop loss / take profit automation
- [ ] Portfolio tracking & PnL analytics
- [ ] Multi-account management
- [ ] Position rebalancing strategies
- [ ] Liquidation monitoring & alerts
- [ ] Integration with unju-agent tool system
- [ ] Integration with unju vault for key management

## License

MIT

## Links

- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)
- [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [unju Platform](https://unju.ai)
