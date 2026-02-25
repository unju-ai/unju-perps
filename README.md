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

## Architecture

See **[RFC-001: MCP Server Architecture](RFC-001-MCP-SERVER.md)** for the complete technical specification.

**Key Design Decisions:**
- MCP server with stdio transport (no web UI)
- Visual feedback via inline images (charts as base64 PNG)
- Built-in risk management and safety controls
- Native LiveKit agent integration

## Roadmap

### Phase 1: Core MCP Server (Week 1)
- [ ] FastMCP server setup
- [ ] Basic trading tools (market_order, get_position, get_balance)
- [ ] Risk management layer

### Phase 2: Visual Feedback (Week 1-2)
- [ ] Chart generation (matplotlib)
- [ ] Dashboard and position charts
- [ ] Base64 image pipeline

### Phase 3: Advanced Tools (Week 2)
- [ ] Close position, market data, risk limits
- [ ] Stop loss / take profit automation

### Phase 4: LiveKit Integration (Week 2-3)
- [ ] Example agent integration
- [ ] Documentation and demos

### Phase 5: Production Hardening (Week 3-4)
- [ ] Error recovery and monitoring
- [ ] Performance optimization
- [ ] Security audit

### Future Enhancements
- [ ] Multi-account management
- [ ] Position rebalancing strategies
- [ ] Liquidation monitoring & alerts
- [ ] Integration with unju vault for key management
- [ ] WebSocket real-time updates
- [ ] Interactive plotly charts

## License

MIT

## Links

- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)
- [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [unju Platform](https://unju.ai)
