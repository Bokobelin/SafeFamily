"""Custom exceptions for the SafeFamily project."""


class SafeFamilyError(Exception):
    """Base exception for the project."""


class AuthenticationError(SafeFamilyError):
    """Raised when authentication fails."""


class DatabaseConnectionError(SafeFamilyError):
    """Raised when database connection fails."""


class RuleExecutionError(SafeFamilyError):
    """Raised when rule execution fails."""


class URLBlockedError(SafeFamilyError):
    """Raised when URL is blocked."""


class NotificationError(SafeFamilyError):
    """Raised when notification sending fails."""
