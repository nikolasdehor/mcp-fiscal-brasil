"""Core public API for mcp-fiscal-brasil."""

from .config import Settings, settings
from .errors import (
    FiscalError,
    FiscalHTTPError,
    FiscalNotFoundError,
    FiscalRateLimitError,
    FiscalValidationError,
)
from .http import HTTPClient
from .logging import get_logger

__all__ = [
    "FiscalError",
    "FiscalHTTPError",
    "FiscalNotFoundError",
    "FiscalRateLimitError",
    "FiscalValidationError",
    "HTTPClient",
    "Settings",
    "get_logger",
    "settings",
]
