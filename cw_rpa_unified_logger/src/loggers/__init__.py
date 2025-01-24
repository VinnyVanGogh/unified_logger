"""
This module provides a unified interface for different logging backends, allowing you to log in multiple formats and to multiple destinations at once.
"""

from .unified import UnifiedLogger
from .config import LoggerConfig
from .types import LoggerType
from .async_logger import AsyncLogger, get_logger
from .setup_loggers import setup_loggers



__all__ = [
    "UnifiedLogger",
    "LoggerConfig",
    "LoggerType",
    "AsyncLogger",
    "get_logger",
    "setup_loggers"
]