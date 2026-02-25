"""Main PerpTrader client"""

from typing import Optional, Union
from datetime import datetime
from eth_account import Account

from unju_perps.types import (
    Order,
    Position,
    Market,
    Balance,
    OrderSide,
    OrderType,
    OrderStatus,
    RiskLimits,
)
from unju_perps.exceptions import (
    InsufficientBalanceError,
    InvalidSymbolError,
    OrderRejectedError,
    RiskLimitExceededError,
    PositionNotFoundError,
)


class PerpTrader:
    """
    Agent-friendly wrapper for Hyperliquid perpetual futures trading.
    
    Provides a clean, opinionated interface for AI agents to trade perps
    with built-in risk management and safety controls.
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        testnet: bool = True,
        risk_limits: Optional[RiskLimits] = None,
    ):
        """
        Initialize PerpTrader.
        
        Args:
            private_key: Ethereum private key (0x prefixed hex)
            testnet: Use Hyperliquid testnet (default: True)
            risk_limits: Risk management limits (default: conservative)
        """
        self.testnet = testnet
        self.risk_limits = risk_limits or RiskLimits()
        
        # TODO: Initialize Hyperliquid SDK
        # from hyperliquid.exchange import Exchange
        # from hyperliquid.info import Info
        
        if private_key:
            self.account = Account.from_key(private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
    
    def market_order(
        self,
        symbol: str,
        side: Union[str, OrderSide],
        size_usd: float,
        slippage_bps: int = 50,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None,
    ) -> Order:
        """
        Place a market order.
        
        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH", "SOL")
            side: "long" or "short"
            size_usd: Position size in USD
            slippage_bps: Max slippage in basis points (default: 50 = 0.5%)
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
        # Normalize side
        if isinstance(side, str):
            side = OrderSide(side.lower())
        
        # TODO: Validate symbol
        # TODO: Check balance
        # TODO: Check risk limits
        # TODO: Calculate size in contracts
        # TODO: Place order via Hyperliquid SDK
        # TODO: Handle response and errors
        
        raise NotImplementedError("market_order() not yet implemented")
    
    def limit_order(
        self,
        symbol: str,
        side: Union[str, OrderSide],
        size_usd: float,
        limit_price: float,
        post_only: bool = False,
        time_in_force: str = "GTC",
    ) -> Order:
        """Place a limit order."""
        raise NotImplementedError("limit_order() not yet implemented")
    
    def close_position(
        self,
        symbol: str,
        slippage_bps: int = 50,
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
        raise NotImplementedError("close_position() not yet implemented")
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for a symbol."""
        raise NotImplementedError("get_position() not yet implemented")
    
    def get_all_positions(self) -> list[Position]:
        """Get all open positions."""
        raise NotImplementedError("get_all_positions() not yet implemented")
    
    def get_balance(self) -> Balance:
        """Get account balance."""
        raise NotImplementedError("get_balance() not yet implemented")
    
    def get_market_data(self, symbol: str) -> Market:
        """Get current market data for a symbol."""
        raise NotImplementedError("get_market_data() not yet implemented")
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        raise NotImplementedError("cancel_order() not yet implemented")
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list[Order]:
        """Get all open orders, optionally filtered by symbol."""
        raise NotImplementedError("get_open_orders() not yet implemented")
