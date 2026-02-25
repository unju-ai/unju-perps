# RFC-001: unju-perps MCP Server Architecture

**Status:** Draft  
**Author:** Green Tara (AI Agent)  
**Created:** 2026-02-25  
**Updated:** 2026-02-25

## Abstract

This RFC proposes the architecture for `unju-perps`, an MCP (Model Context Protocol) server that provides AI agents with tools to trade perpetual futures on Hyperliquid. The server exposes trading operations, portfolio monitoring, and risk management through a standardized MCP interface, with visual feedback delivered as inline images.

## Motivation

### Problem Statement

Current challenges for AI agents trading cryptocurrency perpetuals:

1. **Complex API Integration**: Direct Hyperliquid SDK integration requires agents to handle wallet management, signing, nonce tracking, and error recovery
2. **No Visual Feedback**: Agents cannot show users portfolio charts, P&L graphs, or position visualizations
3. **Limited Safety**: No built-in risk management, position limits, or circuit breakers
4. **Poor Agent UX**: Clunky tool interfaces that require multiple calls for common workflows

### Goals

1. **Agent-First Design**: Simple, intuitive tools optimized for LLM function calling
2. **Visual Output**: Return charts and dashboards as images in MCP responses
3. **Safety by Default**: Built-in risk controls, position limits, and validation
4. **LiveKit Native**: Seamless integration with unju-agent via LiveKit's MCP support

### Non-Goals

1. ~~Web UI for humans~~ (use MCP images instead)
2. ~~REST API~~ (MCP only)
3. ~~Multi-exchange support~~ (Hyperliquid only for v1)
4. ~~Historical data analysis~~ (focus on real-time trading)

## Design

### Architecture Overview

```
┌─────────────────────────────────────┐
│      LiveKit Agent (unju-agent)     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  MCP Client (native)        │   │
│  │  - stdio transport          │   │
│  │  - tool discovery           │   │
│  │  - function calls           │   │
│  └──────────┬──────────────────┘   │
└─────────────┼────────────────────────┘
              │ stdio (JSON-RPC)
              ▼
┌─────────────────────────────────────┐
│      unju-perps MCP Server          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  MCP Tools (FastMCP)        │   │
│  │  - market_order()           │   │
│  │  - get_position()           │   │
│  │  - get_dashboard()          │   │
│  │  - close_position()         │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │  Trading Logic              │   │
│  │  - PerpTrader client        │   │
│  │  - Risk management          │   │
│  │  - Position tracking        │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │  Chart Generation           │   │
│  │  - matplotlib/plotly        │   │
│  │  - PNG/WebP output          │   │
│  │  - base64 encoding          │   │
│  └──────────┬──────────────────┘   │
└─────────────┼────────────────────────┘
              │ HTTPS
              ▼
┌─────────────────────────────────────┐
│      Hyperliquid Exchange           │
└─────────────────────────────────────┘
```

### Project Structure

```
unju-perps/
├── unju_perps/
│   ├── __init__.py
│   ├── server.py           # MCP server (FastMCP)
│   ├── client.py           # Hyperliquid trading logic
│   ├── charts.py           # Chart generation (matplotlib/plotly)
│   ├── types.py            # Order, Position, Market, Balance
│   ├── risk.py             # Risk management & limits
│   ├── exceptions.py       # Custom exceptions
│   └── utils.py            # Helpers (formatting, vault, etc.)
├── tests/
│   ├── test_server.py
│   ├── test_client.py
│   └── test_charts.py
├── examples/
│   └── agent_integration.py
├── pyproject.toml
├── README.md
└── RFC-001-MCP-SERVER.md  # This document
```

### MCP Tools Specification

#### 1. `market_order`

Execute a market order with slippage protection.

**Input Schema:**
```json
{
  "symbol": {
    "type": "string",
    "description": "Asset symbol (BTC, ETH, SOL, etc.)"
  },
  "side": {
    "type": "string",
    "enum": ["long", "short"],
    "description": "Order side"
  },
  "size_usd": {
    "type": "number",
    "minimum": 1,
    "description": "Position size in USD"
  },
  "slippage_bps": {
    "type": "integer",
    "default": 50,
    "description": "Max slippage in basis points (50 = 0.5%)"
  },
  "stop_loss_pct": {
    "type": "number",
    "optional": true,
    "description": "Stop loss percentage from entry"
  },
  "take_profit_pct": {
    "type": "number",
    "optional": true,
    "description": "Take profit percentage from entry"
  }
}
```

**Output:**
```json
{
  "order_id": "1234567890",
  "symbol": "BTC",
  "side": "long",
  "size": 0.01,
  "entry_price": 51234.56,
  "fees_usd": 0.51,
  "timestamp": "2026-02-25T12:00:00Z",
  "message": "✅ Long BTC: $100 @ $51,234.56 (0.01 BTC)"
}
```

#### 2. `get_position`

Get detailed information about a specific position.

**Input Schema:**
```json
{
  "symbol": {
    "type": "string",
    "description": "Asset symbol"
  }
}
```

**Output:**
```json
{
  "symbol": "BTC",
  "side": "long",
  "size": 0.01,
  "entry_price": 51234.56,
  "mark_price": 51500.00,
  "liquidation_price": 46000.00,
  "leverage": 10.0,
  "unrealized_pnl": 2.65,
  "unrealized_pnl_pct": 5.18,
  "margin": 102.47,
  "message": "📊 BTC Long: $100 → $102.65 (+2.65%)"
}
```

#### 3. `get_dashboard`

Generate a visual dashboard with portfolio overview.

**Input Schema:**
```json
{
  "format": {
    "type": "string",
    "enum": ["png", "webp"],
    "default": "png"
  },
  "width": {
    "type": "integer",
    "default": 1200
  },
  "height": {
    "type": "integer",
    "default": 800
  }
}
```

**Output:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "type": "image/png",
  "summary": {
    "total_balance": 10234.56,
    "total_pnl": 234.56,
    "total_pnl_pct": 2.34,
    "open_positions": 3,
    "largest_position": "BTC"
  },
  "message": "💰 Portfolio: $10,234 | P&L: +$234.56 (+2.34%) | 3 positions"
}
```

**Chart Contents:**
- Top panel: Position P&L bar chart
- Middle panel: Portfolio balance over time
- Bottom panel: Active positions table with entry/current/liquidation prices

#### 4. `get_position_chart`

Generate detailed chart for a specific position.

**Input Schema:**
```json
{
  "symbol": {
    "type": "string",
    "description": "Asset symbol"
  },
  "timeframe": {
    "type": "string",
    "enum": ["1h", "4h", "1d"],
    "default": "1h"
  }
}
```

**Output:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "type": "image/png",
  "position": {
    "symbol": "BTC",
    "entry_price": 51234.56,
    "current_price": 51500.00,
    "liquidation_price": 46000.00,
    "pnl": 2.65
  },
  "message": "📈 BTC position: Entry $51,234 → Now $51,500 → Liq $46,000"
}
```

**Chart Contents:**
- Price action with entry marker
- Current price line
- Liquidation price danger zone (red)
- P&L indicator
- Volume bars

#### 5. `close_position`

Close an open position at market price.

**Input Schema:**
```json
{
  "symbol": {
    "type": "string",
    "description": "Asset symbol"
  },
  "slippage_bps": {
    "type": "integer",
    "default": 50,
    "description": "Max slippage in basis points"
  }
}
```

**Output:**
```json
{
  "order_id": "9876543210",
  "symbol": "BTC",
  "size": 0.01,
  "exit_price": 51500.00,
  "realized_pnl": 2.65,
  "realized_pnl_pct": 2.59,
  "fees_usd": 0.51,
  "holding_time": "2h 34m",
  "message": "✅ Closed BTC: +$2.65 (+2.59%) | Held 2h 34m"
}
```

#### 6. `get_balance`

Get account balance and available margin.

**Input Schema:**
```json
{}
```

**Output:**
```json
{
  "total": 10234.56,
  "available": 5000.00,
  "margin_used": 5234.56,
  "unrealized_pnl": 234.56,
  "buying_power": 50000.00,
  "message": "💵 Balance: $10,234 | Available: $5,000 | BP: $50,000"
}
```

#### 7. `get_market_data`

Get current market data for a symbol.

**Input Schema:**
```json
{
  "symbol": {
    "type": "string",
    "description": "Asset symbol"
  }
}
```

**Output:**
```json
{
  "symbol": "BTC",
  "mark_price": 51500.00,
  "index_price": 51498.23,
  "funding_rate": 0.0001,
  "funding_rate_annual": 10.95,
  "open_interest": 1250000000,
  "volume_24h": 5000000000,
  "high_24h": 52000.00,
  "low_24h": 50500.00,
  "change_24h": 1.23,
  "message": "📊 BTC: $51,500 | Funding: 0.01% (10.95% APR) | Vol: $5.0B"
}
```

#### 8. `set_risk_limits`

Configure risk management limits for the account.

**Input Schema:**
```json
{
  "max_position_size_usd": {
    "type": "number",
    "description": "Max position size in USD"
  },
  "max_leverage": {
    "type": "number",
    "minimum": 1,
    "maximum": 50,
    "description": "Max leverage allowed"
  },
  "max_daily_loss_usd": {
    "type": "number",
    "description": "Max daily loss before circuit breaker"
  },
  "allowed_symbols": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Whitelist of allowed symbols (empty = all)"
  }
}
```

**Output:**
```json
{
  "max_position_size_usd": 10000,
  "max_leverage": 10,
  "max_daily_loss_usd": 1000,
  "allowed_symbols": ["BTC", "ETH", "SOL"],
  "message": "🛡️ Risk limits updated: $10k max position, 10x max leverage, $1k daily loss limit"
}
```

### Risk Management

#### Position Limits
- Default: $10,000 max position size
- Default: 10x max leverage
- Configurable per-account via `set_risk_limits`

#### Daily Loss Circuit Breaker
- Default: $1,000 max daily loss
- All trading disabled when limit hit
- Resets at 00:00 UTC
- Can only close positions after trigger

#### Symbol Whitelist
- Optional: restrict trading to specific symbols
- Prevents agents from trading low-liquidity/high-risk assets
- Default: all Hyperliquid-supported symbols allowed

#### Slippage Protection
- Default: 50 bps (0.5%) max slippage
- Orders rejected if slippage exceeds limit
- Configurable per-order

#### Validation
- Balance checks before order placement
- Position size validation
- Leverage limit enforcement
- Symbol whitelist enforcement

### Chart Generation

#### Technology Stack
- **matplotlib** for static charts (simple, fast)
- **plotly** for interactive charts (future enhancement)
- **Pillow** for image processing
- Output: PNG or WebP format
- Encoding: base64 for MCP transmission

#### Chart Types

**Dashboard:**
- Style: Clean, professional, unju.ai branding
- Resolution: 1200x800 @ 150 DPI
- Components:
  - Position P&L bars (green/red)
  - Balance line chart (7d history)
  - Positions table (symbol, entry, current, liq, P&L)
  - Summary metrics header

**Position Chart:**
- Style: Trading view inspired
- Resolution: 1000x600 @ 150 DPI
- Components:
  - Candlestick/line price chart
  - Entry price horizontal line (blue)
  - Current price marker
  - Liquidation zone (red shaded)
  - P&L annotation
  - Volume bars

#### Performance
- Cache rendered charts (5 second TTL)
- Lazy load chart libraries
- Async rendering
- Target: <500ms chart generation

### Security

#### Private Key Management
- Environment variable: `HYPERLIQUID_PRIVATE_KEY`
- Optional: Integration with unju vault system (future)
- Never logged or exposed in responses
- Testnet mode for safe development

#### API Security
- User-Agent header: `unju-perps/{version}`
- Rate limiting handled by Hyperliquid
- Exponential backoff on errors
- Connection pooling

#### Agent Security
- MCP server runs in isolated process
- No network access except Hyperliquid API
- File system access limited to config
- Memory limits enforced

### Testing Strategy

#### Unit Tests
- Mock Hyperliquid API responses
- Test all MCP tools independently
- Risk limit enforcement
- Chart generation

#### Integration Tests
- Connect to Hyperliquid testnet
- End-to-end order placement
- Position management
- Balance queries

#### Agent Integration Tests
- LiveKit agent connection
- Tool discovery
- Function calling
- Image rendering in chat

### Deployment

#### Installation
```bash
pip install unju-perps
```

#### Configuration
```bash
export HYPERLIQUID_PRIVATE_KEY="0x..."
export HYPERLIQUID_TESTNET="true"  # optional
```

#### Running MCP Server
```bash
uv run unju-perps
# or
python -m unju_perps.server
```

#### LiveKit Agent Integration
```python
# In unju-agent
from livekit.agents import mcp

perps = mcp.connect(
    "stdio",
    command="uv",
    args=["run", "unju-perps"]
)

# Tools automatically available
tools = await perps.list_tools()
```

#### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "unju-perps": {
      "command": "uv",
      "args": ["run", "unju-perps"],
      "env": {
        "HYPERLIQUID_PRIVATE_KEY": "0x...",
        "HYPERLIQUID_TESTNET": "true"
      }
    }
  }
}
```

## Alternatives Considered

### Alternative 1: Web UI + REST API

**Approach:** Build a web server with REST API and browser UI.

**Pros:**
- Human-friendly interface
- Direct browser access
- Standard HTTP patterns

**Cons:**
- Requires separate deployment
- Agents need HTTP client
- More complex architecture
- Two interfaces to maintain
- Network dependency

**Rejected because:** MCP with images provides better agent UX and simpler architecture.

### Alternative 2: Multi-Exchange Support

**Approach:** Support multiple DEXs (dYdX, GMX, etc.) via unified interface.

**Pros:**
- More flexibility
- Best execution across venues
- Redundancy

**Cons:**
- Complex abstraction layer
- Different API patterns
- More maintenance burden
- Increases scope significantly

**Deferred because:** Focus on Hyperliquid first, add exchanges later if needed.

### Alternative 3: Historical Analysis Tools

**Approach:** Add tools for backtesting, performance analytics, trade journaling.

**Pros:**
- Better decision making
- Performance tracking
- Learning from history

**Cons:**
- Scope creep
- Database required
- Complex queries
- Not core to trading

**Deferred because:** Focus on real-time trading first, add analytics later.

### Alternative 4: Direct SDK in Agent

**Approach:** Import Hyperliquid SDK directly in agent code.

**Pros:**
- No separate server
- Simpler deployment
- Fewer moving parts

**Cons:**
- Agent needs wallet management
- No safety layer
- Hard to share across agents
- Complex error handling
- No visual feedback

**Rejected because:** MCP abstraction provides better safety and UX.

## Implementation Plan

### Phase 1: Core MCP Server (Week 1)
- [ ] FastMCP server setup
- [ ] Hyperliquid SDK integration
- [ ] Basic tools: `market_order`, `get_position`, `get_balance`
- [ ] Risk management layer
- [ ] Unit tests

### Phase 2: Visual Feedback (Week 1-2)
- [ ] matplotlib chart generation
- [ ] Dashboard chart
- [ ] Position chart
- [ ] base64 encoding pipeline
- [ ] Chart caching

### Phase 3: Advanced Tools (Week 2)
- [ ] `close_position`
- [ ] `get_market_data`
- [ ] `set_risk_limits`
- [ ] Stop loss / take profit automation
- [ ] Integration tests

### Phase 4: LiveKit Integration (Week 2-3)
- [ ] Example agent integration
- [ ] Tool discovery validation
- [ ] Chat image rendering
- [ ] Documentation
- [ ] Demo video

### Phase 5: Production Hardening (Week 3-4)
- [ ] Error recovery
- [ ] Logging to stderr
- [ ] Connection pooling
- [ ] Rate limit handling
- [ ] Performance optimization
- [ ] Security audit

## Open Questions

1. **Chart library choice**: matplotlib (simple, fast) vs plotly (interactive)?
   - **Recommendation**: Start with matplotlib, add plotly later for interactive charts

2. **Image format**: PNG (universal) vs WebP (smaller)?
   - **Recommendation**: PNG default, WebP optional for bandwidth optimization

3. **Vault integration**: When to add secure key management?
   - **Recommendation**: Phase 6 after core features stable

4. **Multi-account support**: Should one server support multiple trading accounts?
   - **Recommendation**: One server per account initially, add multi-account later

5. **Real-time updates**: Should positions auto-update via websocket?
   - **Recommendation**: Polling initially, websocket in Phase 6

## Success Metrics

### Agent UX
- Tool call success rate: >99%
- Average response time: <500ms
- Chart generation time: <500ms
- Error recovery rate: >95%

### Trading Performance
- Order fill rate: >98%
- Slippage within limits: >99%
- Risk limit enforcement: 100%
- Zero unauthorized trades

### Adoption
- Used by >3 unju.ai agents
- >100 trades executed in first month
- Zero security incidents
- Positive agent feedback

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [LiveKit Agents MCP Support](https://docs.livekit.io/agents/)
- [Hyperliquid API Documentation](https://hyperliquid.gitbook.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [unju-agent Repository](https://github.com/unju-ai/unju-agent)

## Changelog

- **2026-02-25**: Initial draft (Green Tara)
