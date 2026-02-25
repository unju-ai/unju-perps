# unju-perps

**MCP Server for AI agents to trade perpetual futures on Hyperliquid**

An MCP (Model Context Protocol) server with interactive HTML UIs that makes it dead simple for AI agents to trade perps on Hyperliquid. Built with the [MCP Apps extension](https://github.com/modelcontextprotocol/ext-apps) for rich, interactive experiences inside chat clients.

## Features

- 🤖 **Agent-First API** — MCP tools designed for LLM function calling
- 🎨 **Interactive UIs** — Real-time charts, forms, dashboards via MCP Apps
- 🔐 **Secure by default** — Wallet management, signing, nonce handling
- 📊 **Rich market data** — Positions, orders, funding, liquidations
- ⚡ **Fast execution** — Minimal overhead over raw Hyperliquid SDK
- 🛡️ **Risk controls** — Position limits, max leverage, circuit breakers
- 🔄 **Bidirectional** — UIs can call tools back to server for actions
- 🌓 **Theme aware** — Light/dark mode support

## Quick Start

### As MCP Server (for agents)

```bash
# Install
pip install unju-perps

# Configure environment
export HYPERLIQUID_PRIVATE_KEY="0x..."
export HYPERLIQUID_TESTNET="true"

# Run server
uv run unju-perps --stdio
```

### In LiveKit Agent

```python
from livekit.agents import mcp

# Connect to MCP server
perps = mcp.connect("stdio", command="uv", args=["run", "unju-perps", "--stdio"])

# Agent conversation flow:
# User: "Show me my trading portfolio"
# Agent: *calls get_dashboard() tool*
# Host: *renders interactive dashboard UI with live charts*
# User: *clicks "Close Position" button in UI*
# UI: *calls close_position() tool*
# Agent: "Position closed! Realized P&L: +$42.50"
```

### As Python Library (direct use)

```python
from unju_perps import PerpTrader

trader = PerpTrader(private_key="0x...", testnet=True)

# Place order
order = trader.market_order(symbol="BTC", side="long", size_usd=100.0)

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

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "unju-perps": {
      "command": "uv",
      "args": ["run", "unju-perps", "--stdio"],
      "env": {
        "HYPERLIQUID_PRIVATE_KEY": "0x...",
        "HYPERLIQUID_TESTNET": "true"
      }
    }
  }
}
```

## Architecture

```
unju-perps/
├── unju_perps/
│   ├── __init__.py
│   ├── server.py          # MCP server (FastMCP + UI resources)
│   ├── client.py          # Hyperliquid trading logic
│   ├── views/             # Interactive HTML UIs (MCP Apps)
│   │   ├── dashboard.html # Portfolio overview with live charts
│   │   ├── position.html  # Position detail with interactive chart
│   │   └── risk.html      # Risk configuration form
│   ├── types.py           # Order, Position, Market types
│   ├── risk.py            # Risk management & limits
│   ├── utils.py           # Helpers (vault integration, etc.)
│   └── exceptions.py      # Custom exceptions
├── tests/
└── examples/
```

### MCP Tools

1. **`market_order`** - Execute market orders with slippage protection
2. **`get_position`** - Get position details **+ interactive chart UI**
3. **`get_dashboard`** - Portfolio overview **+ interactive dashboard UI**
4. **`close_position`** - Close positions at market
5. **`get_balance`** - Account balance and margin info
6. **`get_market_data`** - Real-time market data
7. **`configure_risk`** - Risk limits **+ interactive config form**

### Interactive UIs

UIs render inline in chat clients via [MCP Apps extension](https://github.com/modelcontextprotocol/ext-apps):

- **Dashboard**: Live P&L charts, balance history, positions table with action buttons
- **Position View**: Interactive price chart with entry/current/liquidation markers, "Close" button
- **Risk Config**: Form to configure position limits, leverage, circuit breakers

## MCP Apps Integration

Tools with UIs automatically render interactive views in the chat:

**User:** "Show me my portfolio"

**Agent:** *calls `get_dashboard()` tool*

**Host:** *fetches `ui://perps/dashboard` resource and renders in iframe*

**UI View:** 
- Live balance/P&L metrics
- Position P&L bar chart (plotly)
- Balance history line chart
- Positions table with "Close" buttons

**User:** *clicks "Close" button on BTC position*

**UI:** *calls `close_position("BTC")` tool via MCP Apps SDK*

**Agent:** "Position closed! Realized P&L: +$42.50 (+2.3%)"

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
