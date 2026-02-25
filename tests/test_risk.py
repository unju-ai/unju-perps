"""Tests for risk management"""

import pytest
from unju_perps.risk import RiskManager
from unju_perps.types import RiskLimits, Position, OrderSide
from unju_perps.exceptions import RiskLimitExceededError
from datetime import datetime


def test_position_size_limit():
    """Test position size limit enforcement"""
    limits = RiskLimits(max_position_size_usd=1000.0)
    risk = RiskManager(limits)
    
    # Should pass
    risk.check_position_size("BTC", 500.0, [])
    
    # Should fail
    with pytest.raises(RiskLimitExceededError):
        risk.check_position_size("BTC", 2000.0, [])


def test_leverage_limit():
    """Test leverage limit enforcement"""
    limits = RiskLimits(max_leverage=10.0)
    risk = RiskManager(limits)
    
    # Should pass
    risk.check_leverage(5.0)
    
    # Should fail
    with pytest.raises(RiskLimitExceededError):
        risk.check_leverage(20.0)


def test_symbol_allowlist():
    """Test symbol allowlist enforcement"""
    limits = RiskLimits(allowed_symbols=["BTC", "ETH"])
    risk = RiskManager(limits)
    
    # Should pass
    risk.check_symbol_allowed("BTC")
    
    # Should fail
    with pytest.raises(RiskLimitExceededError):
        risk.check_symbol_allowed("DOGE")
