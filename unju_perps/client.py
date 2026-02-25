"""
Hyperliquid trading client
"""
from typing import Optional, List
from datetime import datetime, timedelta
from eth_account import Account

from .types import (
    Order,
    Position,
    Market,
    Balance,
    OrderSide,
    OrderType,
    OrderStatus,
    RiskLimits
)
from .risk import RiskManager
from .exceptions import (
    InsufficientBalanceError,
    InvalidSymbolError,
    OrderRejectedError,
    PositionNotFoundError
)


class PerpTrader:
    """
    Agent-friendly wrapper for Hyperliquid perpetual futures trading.
    
    Provides a clean interface for AI agents to trade perps with built-in
    risk management and safety controls.
    """
    
    def __init__(
        self,
        private_key: str,
        testnet: bool = True,
        risk_limits: Optional[RiskLimits] = None
    ):
        """
        Initialize PerpTrader.
        
        Args:
            private_key: Ethereum private key (0x prefixed hex)
            testnet: Use Hyperliquid testnet (default: True)
            risk_limits: Risk management limits
        """
        self.testnet = testnet
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        # Initialize risk manager
        self.risk_manager = RiskManager(risk_limits or RiskLimits())
        
        # TODO: Initialize Hyperliquid SDK
        # from hyperliquid.exchange import Exchange
        # from hyperliquid.info import Info
        # self.exchange = Exchange(wallet=self.account, testnet=testnet)
        # self.info = Info(testnet=testnet)
        
        # For now, use mock data
        self._mock_balance = 10000.0
        self._mock_positions: List[Position] = []
    
    def market_order(
        self,
        symbol: str,
        side: OrderSide,
        size_usd: float,
        slippage_bps: int = 50,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None
    ) -> Order:
        """
        Place a market order.
        
        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH")
            side: Order side (long or short)
            size_usd: Position size in USD
            slippage_bps: Max slippage in basis points
            stop_loss_pct: Optional stop loss percentage
            take_profit_pct: Optional take profit percentage
        
        Returns:
            Order object with execution details
        
        Raises:
            InvalidSymbolError: Symbol not supported
            InsufficientBalanceError: Not enough balance
            RiskLimitExceededError: Would exceed risk limits
            OrderRejectedError: Exchange rejected the order
        """
        # Validate symbol
        symbol = symbol.upper()
        if symbol not in ["BTC", "ETH", "SOL", "ARB", "AVAX"]:
            raise InvalidSymbolError(f"Symbol {symbol} not supported")
        
        # Check balance
        required_margin = size_usd / 10  # Assuming 10x leverage
        if required_margin > self._mock_balance:
            raise InsufficientBalanceError(
                f"Insufficient balance. Required: ${required_margin:.2f}, Available: ${self._mock_balance:.2f}"
            )
        
        # Check risk limits
        self.risk_manager.check_position_size(symbol, size_usd, self._mock_positions)
        self.risk_manager.check_leverage(10.0)
        self.risk_manager.check_symbol_allowed(symbol)
        
        # TODO: Place order via Hyperliquid SDK
        # result = self.exchange.market_order(...)
        
        # Mock order response
        mock_price = self._get_mock_price(symbol)
        order = Order(
            id=f"order_{datetime.utcnow().timestamp()}",
            symbol=symbol,
            side=side,
            type=OrderType.MARKET,
            size=size_usd / mock_price,
            filled_size=size_usd / mock_price,
            average_price=mock_price,
            status=OrderStatus.FILLED,
            timestamp=datetime.utcnow(),
            fees=size_usd * 0.0005  # 0.05% fee
        )
        
        # Update mock balance
        self._mock_balance -= required_margin
        
        # Create position
        position = Position(
            symbol=symbol,
            side=side,
            size=order.filled_size,
            entry_price=order.average_price,
            mark_price=mock_price,
            liquidation_price=self._calculate_liquidation_price(
                mock_price, 10.0, side.value
            ),
            leverage=10.0,
            unrealized_pnl=0.0,
            margin=required_margin,
            timestamp=datetime.utcnow()
        )
        self._mock_positions.append(position)
        
        return order
    
    def close_position(
        self,
        symbol: str,
        slippage_bps: int = 50
    ) -> Order:
        """
        Close an open position.
        
        Args:
            symbol: Asset symbol
            slippage_bps: Max slippage in basis points
        
        Returns:
            Order object for the closing trade
        
        Raises:
            PositionNotFoundError: No open position for symbol
        """
        position = self.get_position(symbol)
        if not position:
            raise PositionNotFoundError(f"No open position for {symbol}")
        
        # TODO: Close position via Hyperliquid SDK
        
        # Mock close order
        mock_price = self._get_mock_price(symbol)
        close_side = OrderSide.SHORT if position.side == OrderSide.LONG else OrderSide.LONG
        
        order = Order(
            id=f"order_{datetime.utcnow().timestamp()}",
            symbol=symbol,
            side=close_side,
            type=OrderType.MARKET,
            size=position.size,
            filled_size=position.size,
            average_price=mock_price,
            status=OrderStatus.FILLED,
            timestamp=datetime.utcnow(),
            fees=position.size * mock_price * 0.0005
        )
        
        # Calculate PnL
        if position.side == OrderSide.LONG:
            pnl = (mock_price - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - mock_price) * position.size
        
        # Update mock balance
        self._mock_balance += position.margin + pnl - order.fees
        
        # Remove position
        self._mock_positions = [p for p in self._mock_positions if p.symbol != symbol]
        
        return order
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for a symbol."""
        for position in self._mock_positions:
            if position.symbol == symbol:
                # Update mark price and PnL
                mock_price = self._get_mock_price(symbol)
                position.mark_price = mock_price
                
                if position.side == OrderSide.LONG:
                    position.unrealized_pnl = (mock_price - position.entry_price) * position.size
                else:
                    position.unrealized_pnl = (position.entry_price - mock_price) * position.size
                
                return position
        
        return None
    
    def get_all_positions(self) -> List[Position]:
        """Get all open positions."""
        # Update all positions with current prices
        for position in self._mock_positions:
            mock_price = self._get_mock_price(position.symbol)
            position.mark_price = mock_price
            
            if position.side == OrderSide.LONG:
                position.unrealized_pnl = (mock_price - position.entry_price) * position.size
            else:
                position.unrealized_pnl = (position.entry_price - mock_price) * position.size
        
        return self._mock_positions
    
    def get_balance(self) -> Balance:
        """Get account balance."""
        positions = self.get_all_positions()
        unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        margin_used = sum(p.margin for p in positions)
        
        return Balance(
            total=self._mock_balance + margin_used + unrealized_pnl,
            available=self._mock_balance,
            margin_used=margin_used,
            unrealized_pnl=unrealized_pnl,
            timestamp=datetime.utcnow()
        )
    
    def get_market_data(self, symbol: str) -> Market:
        """Get current market data for a symbol."""
        mock_price = self._get_mock_price(symbol)
        
        return Market(
            symbol=symbol,
            mark_price=mock_price,
            index_price=mock_price * 0.9999,
            funding_rate=0.0001,
            open_interest=1000000.0,
            volume_24h=50000000.0,
            high_24h=mock_price * 1.02,
            low_24h=mock_price * 0.98,
            change_24h=1.5,
            timestamp=datetime.utcnow()
        )
    
    def get_price_history(self, symbol: str, hours: int = 4) -> List[dict]:
        """Get price history for charting."""
        mock_price = self._get_mock_price(symbol)
        history = []
        
        for i in range(hours * 12):  # 5-minute intervals
            time = datetime.utcnow() - timedelta(minutes=(hours * 60) - (i * 5))
            # Add some random variance
            variance = (i % 10 - 5) * mock_price * 0.001
            history.append({
                "time": time.strftime("%H:%M"),
                "price": mock_price + variance
            })
        
        return history
    
    def get_balance_history(self, days: int = 7) -> List[dict]:
        """Get balance history for charting."""
        current_balance = self.get_balance().total
        history = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i - 1)
            # Simulate some growth
            balance = current_balance * (1 - (days - i) * 0.01)
            history.append({
                "time": date.strftime("%Y-%m-%d"),
                "balance": balance
            })
        
        return history
    
    def _get_mock_price(self, symbol: str) -> float:
        """Get mock price for symbol."""
        prices = {
            "BTC": 51234.56,
            "ETH": 2345.67,
            "SOL": 123.45,
            "ARB": 1.23,
            "AVAX": 45.67
        }
        return prices.get(symbol, 100.0)
    
    def _calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: float,
        side: str
    ) -> float:
        """Calculate liquidation price."""
        maintenance_margin = 0.005  # 0.5%
        
        if side == "long":
            return entry_price * (1 - (1 / leverage) + maintenance_margin)
        else:
            return entry_price * (1 + (1 / leverage) - maintenance_margin)
