"""
This module provides a unified interface for different logging backends, allowing you to log in multiple formats and to multiple destinations at once.
"""

from .unified import UnifiedLogger
from .config import LoggerConfig
from .types import LoggerType

__all__ = [
    "UnifiedLogger",
    "LoggerConfig",
    "LoggerType"
]