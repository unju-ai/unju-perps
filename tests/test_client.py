"""Tests for PerpTrader client"""

import pytest
from unju_perps import PerpTrader
from unju_perps.types import RiskLimits


def test_init_without_key():
    """Test initialization without private key"""
    trader = PerpTrader(testnet=True)
    assert trader.testnet is True
    assert trader.account is None


def test_init_with_risk_limits():
    """Test initialization with custom risk limits"""
    limits = RiskLimits(
        max_position_size_usd=5000.0,
        max_leverage=5.0,
    )
    trader = PerpTrader(testnet=True, risk_limits=limits)
    assert trader.risk_limits.max_position_size_usd == 5000.0
    assert trader.risk_limits.max_leverage == 5.0


# TODO: Add more tests once Hyperliquid SDK integration is complete
