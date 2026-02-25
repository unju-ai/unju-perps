"""Risk management utilities"""

from typing import Optional
from unju_perps.types import Position, RiskLimits
from unju_perps.exceptions import RiskLimitExceededError


class RiskManager:
    """Enforce risk limits on trading operations"""
    
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self.daily_pnl = 0.0  # Track daily P&L
    
    def check_position_size(self, symbol: str, size_usd: float, current_positions: list[Position]) -> None:
        """
        Verify new position wouldn't exceed size limits.
        
        Raises:
            RiskLimitExceededError: Position size exceeds limit
        """
        if size_usd > self.limits.max_position_size_usd:
            raise RiskLimitExceededError(
                f"Position size ${size_usd:.2f} exceeds max ${self.limits.max_position_size_usd:.2f}"
            )
        
        # Check total exposure across all positions
        total_exposure = sum(p.size * p.mark_price for p in current_positions) + size_usd
        max_total_exposure = self.limits.max_position_size_usd * 5  # 5x single position limit
        
        if total_exposure > max_total_exposure:
            raise RiskLimitExceededError(
                f"Total exposure ${total_exposure:.2f} exceeds max ${max_total_exposure:.2f}"
            )
    
    def check_leverage(self, leverage: float) -> None:
        """
        Verify leverage is within limits.
        
        Raises:
            RiskLimitExceededError: Leverage exceeds limit
        """
        if leverage > self.limits.max_leverage:
            raise RiskLimitExceededError(
                f"Leverage {leverage}x exceeds max {self.limits.max_leverage}x"
            )
    
    def check_daily_loss(self, potential_loss: float) -> None:
        """
        Verify daily loss limit not exceeded.
        
        Raises:
            RiskLimitExceededError: Daily loss limit exceeded
        """
        if self.daily_pnl + potential_loss < -self.limits.max_daily_loss_usd:
            raise RiskLimitExceededError(
                f"Daily loss limit ${self.limits.max_daily_loss_usd:.2f} would be exceeded"
            )
    
    def check_symbol_allowed(self, symbol: str) -> None:
        """
        Verify symbol is in allowlist (if configured).
        
        Raises:
            RiskLimitExceededError: Symbol not allowed
        """
        if self.limits.allowed_symbols and symbol not in self.limits.allowed_symbols:
            raise RiskLimitExceededError(
                f"Symbol {symbol} not in allowed list: {self.limits.allowed_symbols}"
            )
    
    def update_daily_pnl(self, pnl: float) -> None:
        """Update daily P&L tracker."""
        self.daily_pnl += pnl
    
    def reset_daily_pnl(self) -> None:
        """Reset daily P&L (call at day rollover)."""
        self.daily_pnl = 0.0
