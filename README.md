# unju-perps

**MCP Server for AI agents to trade perpetual futures on Hyperliquid**

An MCP (Model Context Protocol) server with interactive HTML UIs that makes it dead simple for AI agents to trade perps on Hyperliquid. Built with the [MCP Apps extension](https://github.com/modelcontextprotocol/ext-apps) for rich, interactive experiences inside chat clients.

## Features

- 🤖 **Agent-First API** — MCP tools designed for LLM function calling
- 🎨 **Interactive UIs** — Real-time charts, forms, dashboards via MCP Apps
- 🔐 **Magic Wallets** — Secure server wallets with unju credits payment
- 💳 **Credits System** — 1 credit to create wallet, 10 credits/year rent
- 📊 **Rich market data** — Positions, orders, funding, liquidations
- ⚡ **Fast execution** — Minimal overhead over raw Hyperliquid SDK
- 🛡️ **Risk controls** — Position limits, max leverage, circuit breakers
- 🔄 **Bidirectional** — UIs can call tools back to server for actions
- 🌓 **Theme aware** — Light/dark mode support

## Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/unju-ai/unju-perps.git
cd unju-perps

# Install dependencies
pip install -e .
```

### Run the MCP Server

```bash
# For testing with mock data (no real trading)
python -m unju_perps --stdio

# Or with uv
uv run unju-perps --stdio
```

### Configure Environment

For real trading (not yet implemented):

```bash
export MAGIC_API_KEY="your_magic_api_key"
export HYPERLIQUID_TESTNET="true"  # Use testnet
```

## Usage

### In Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "unju-perps": {
      "command": "uv",
      "args": ["--directory", "/path/to/unju-perps", "run", "python", "-m", "unju_perps", "--stdio"],
      "env": {
        "HYPERLIQUID_TESTNET": "true"
      }
    }
  }
}
```

### In LiveKit Agent

```python
from livekit.agents import mcp

# Connect to MCP server
perps = mcp.connect(
    "stdio",
    command="uv",
    args=["--directory", "/path/to/unju-perps", "run", "python", "-m", "unju_perps", "--stdio"]
)

# Agent conversation flow:
# User: "Show me my trading portfolio"
# Agent: *calls get_dashboard() tool*
# Host: *renders interactive dashboard UI with live charts*
# User: *clicks "Close Position" button in UI*
# UI: *calls close_position() tool*
# Agent: "Position closed! Realized P&L: +$42.50"
```

### Test with HTTP Server

For local testing without an MCP client:

```bash
# Start HTTP server
python -m unju_perps

# Server listens on http://localhost:3001/mcp
```

## MCP Tools

### Wallet Management

1. **`wallet_setup`** - Create/manage Magic wallet **+ wallet UI**
   - Create wallet (1 credit)
   - Fund wallet
   - Check status

### Trading Tools

2. **`market_order`** - Execute market orders with slippage protection
3. **`get_position`** - Get position details **+ interactive chart UI**
4. **`get_dashboard`** - Portfolio overview **+ interactive dashboard UI**
5. **`close_position`** - Close positions at market
6. **`get_balance`** - Account balance and margin info
7. **`get_market_data`** - Real-time market data
8. **`configure_risk`** - Risk limits **+ interactive config form**

## Interactive UIs

UIs render inline in chat clients via [MCP Apps extension](https://github.com/modelcontextprotocol/ext-apps):

### Dashboard UI (`ui://perps/dashboard`)
- Live balance/P&L metrics
- Position P&L bar chart (plotly)
- Balance history line chart (7 days)
- Positions table with action buttons
- "Close Position", "Risk Settings", "Wallet Status" buttons
- Auto-refresh every N seconds

### Wallet UI (`ui://perps/wallet-setup`)
- Create wallet with email
- Funding instructions
- Cost breakdown (1 credit + 10/year rent)
- Wallet status display

### Position View (`ui://perps/position`)
- Interactive price chart with entry/current/liquidation markers
- "Close Position" button
- "Set Stop Loss" button
- *(Coming soon)*

### Risk Config (`ui://perps/risk-config`)
- Form to configure position limits, leverage, circuit breakers
- Visual warnings for breach
- "Save" and "Reset" buttons
- *(Coming soon)*

## Architecture

```
unju-perps/
├── unju_perps/
│   ├── server.py          # MCP server (FastMCP + UI resources)
│   ├── client.py          # Hyperliquid trading logic (mock for now)
│   ├── wallet.py          # Magic wallet + unju credits integration
│   ├── views/             # Interactive HTML UIs (MCP Apps)
│   │   ├── dashboard.html # Portfolio overview with live charts
│   │   ├── wallet.html    # Wallet setup and management
│   │   ├── position.html  # Position detail (coming soon)
│   │   └── risk.html      # Risk config form (coming soon)
│   ├── types.py           # Order, Position, Market types
│   ├── risk.py            # Risk management & limits
│   ├── utils.py           # Helpers
│   └── exceptions.py      # Custom exceptions
├── tests/                 # Unit tests
├── examples/              # Example integrations
├── pyproject.toml
└── README.md
```

## Credits System

### Wallet Creation
- **Cost**: 1 unju-credit
- Creates secure Magic server wallet
- Non-custodial, user controls via email

### Wallet Rent
- **Cost**: 10 unju-credits/year
- Keeps wallet active and usable
- Auto-charged annually
- Grace period before deactivation

### Getting Credits
*(Integration with unju-python SDK coming soon)*

## Development Status

### ✅ Phase 1: Core MCP Server (Complete)
- [x] FastMCP server with stdio transport
- [x] Mock trading client (Hyperliquid SDK integration coming)
- [x] Basic tools: `wallet_setup`, `market_order`, `get_position`, `get_dashboard`, `close_position`, `get_balance`, `get_market_data`, `configure_risk`
- [x] Risk management layer
- [x] Wallet management stub (Magic integration coming)
- [x] Dashboard UI (MCP Apps)
- [x] Wallet UI (MCP Apps)

### 🚧 Phase 2: Production Integration (In Progress)
- [ ] Real Hyperliquid SDK integration
- [ ] Magic wallet API integration
- [ ] unju-python SDK integration (credits)
- [ ] Position detail UI
- [ ] Risk configuration UI
- [ ] Automated tests
- [ ] Error handling & recovery

### 📋 Phase 3: Advanced Features (Planned)
- [ ] Stop loss / take profit automation
- [ ] WebSocket real-time updates
- [ ] Multi-account support
- [ ] Position rebalancing strategies
- [ ] Liquidation monitoring
- [ ] Historical analytics

## Security

- **Private Keys**: Managed by Magic (server-side wallets)
- **API Security**: Rate limiting, exponential backoff
- **MCP Apps**: Sandboxed iframes with CSP restrictions
- **Risk Controls**: Position limits, leverage caps, circuit breakers
- **Testnet First**: All development on testnet

## License

MIT

## Links

- [RFC-001: MCP Server Architecture](RFC-001-MCP-SERVER.md)
- [MCP Apps Extension](https://github.com/modelcontextprotocol/ext-apps)
- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)
- [Magic Docs](https://magic.link/docs)
- [unju Platform](https://unju.ai)
