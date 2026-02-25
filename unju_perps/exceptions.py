"""Custom exceptions for unju-perps"""


class UnjuPerpsError(Exception):
    """Base exception for unju-perps"""
    pass


class InsufficientBalanceError(UnjuPerpsError):
    """Raised when account has insufficient balance"""
    pass


class InvalidSymbolError(UnjuPerpsError):
    """Raised when symbol is not supported"""
    pass


class OrderRejectedError(UnjuPerpsError):
    """Raised when order is rejected by exchange"""
    pass


class RiskLimitExceededError(UnjuPerpsError):
    """Raised when action would exceed risk limits"""
    pass


class PositionNotFoundError(UnjuPerpsError):
    """Raised when position doesn't exist"""
    pass


class ConnectionError(UnjuPerpsError):
    """Raised when connection to exchange fails"""
    pass
