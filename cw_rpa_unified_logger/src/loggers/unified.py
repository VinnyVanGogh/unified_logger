#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/unified.py

import logging
from contextlib import contextmanager
import functools
from typing import Any, Generator, Callable
from collections.abc import Callable

from cw_rpa_unified_logger.src.loggers.base import BaseLogger
from cw_rpa_unified_logger.src.loggers.local import LocalLogger
from cw_rpa_unified_logger.src.loggers.asio import AsioLogger
from cw_rpa_unified_logger.src.loggers.discord import DiscordLogger
from cw_rpa_unified_logger.src.loggers.message_formatter import MessageFormatter
from cw_rpa_unified_logger.src.loggers.config import LoggerConfig
from cw_rpa_unified_logger.src.loggers.types import LoggerType

class UnifiedLogger:
    """
    Unified logging system orchestrating multiple logging backends.
    Provides a simple interface while managing complexity internally.
    """
    
    def __init__(self, config: LoggerConfig):
        """
        Initialize unified logger with configuration.
        
        Args:
            config (LoggerConfig): Logger configuration
        """
        self.config = config
        self.formatter = MessageFormatter(
            config.max_message_length,
            config.filter_patterns
        )
        self.loggers: dict[str, BaseLogger] = {}
        
        self._initializes()
        
    def _initializes(self) -> None:
        """Initialize configured logging backends."""
        try:
            print(f"Initializing loggers: {self.config.enabled_loggers}")
            if LoggerType.LOCAL in self.config.enabled_loggers:
                self.loggers["local"] = LocalLogger(self.config)
            if LoggerType.ASIO in self.config.enabled_loggers:
                self.loggers["asio"] = AsioLogger()
            if LoggerType.DISCORD in self.config.enabled_loggers:
                self.loggers["discord"] = DiscordLogger(
                    self.config.discord_webhook_url,
                    self.config.logger_name
                )
        except Exception as e:
            logging.error(f"Failed to initialize loggers: {e}")
            
    def update_config(self, **kwargs) -> None:
        """
        Update logger configuration dynamically.
        
        Args:
            **kwargs: Configuration overrides
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                
        self._initializes()
            
    def _log_to_all(self, level: int, message: str) -> None:
        """
        Distribute log message to all active backends.
        
        Args:
            level (int): Logging level
            message (str): Message to log
        """
        processed = self.formatter.process_message(message)
        if processed is None:
            return
            
        for logger in self.loggers.values():
            try:
                logger.log(level, processed)
            except Exception as e:
                print(f"Logging failed for {logger.__class__.__name__}: {e}")

    @contextmanager
    def temp_config(self, **kwargs) -> Generator[None, None, None]:
        """
        Temporarily modify logger configuration.
        
        Args:
            **kwargs: Configuration overrides
            
        Example:
            with logger.temp_config(log_level=logging.DEBUG):
                logger.debug("Temporary debug message")
        """
        original = {}
        try:
            for key, new_value in kwargs.items():
                original[key] = getattr(self.config, key)
                
            self.config.update(**kwargs)
            yield
        finally:
            self.config.update(**original)

    def with_debug(self, func: Callable | None = None) -> Callable | None:
        """
        Decorator for temporary debug logging.
        
        Example:
            @logger.with_debug
            def process_data():
                logger.debug("Processing...")
        """
        if func is None:
            return self._DebugContext(self)
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.temp_config(log_level=logging.DEBUG):
                return func(*args, **kwargs)
        return wrapper

    class _DebugContext:
        """Context manager for temporary debug mode."""
        def __init__(self, logger: "UnifiedLogger"):
            self.logger = logger
            
        def __enter__(self):
            self.logger.config.update(log_level=logging.DEBUG)
            return self.logger
            
        def __exit__(self, *args):
            self.logger.config.update(log_level=logging.INFO)

    def cleanup(self) -> None:
        """Clean up all logger resources."""
        for logger in self.loggers.values():
            try:
                logger.cleanup()
            except Exception as e:
                print(f"Cleanup failed for {logger.__class__.__name__}: {e}")

    # Standard logging methods
    def debug(self, message: str) -> None:
        """Log debug message."""
        self._log_to_all(logging.DEBUG, message)

    def info(self, message: str) -> None:
        """Log info message."""
        self._log_to_all(logging.INFO, message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self._log_to_all(logging.WARNING, message)

    def error(self, message: str) -> None:
        """Log error message."""
        self._log_to_all(logging.ERROR, message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self._log_to_all(logging.CRITICAL, message)

    def exception(self, e: Exception, message: str = "") -> None:
        """Log exception with context."""
        error_msg = f"{message + ': ' if message else ''}{str(e)}"
        self._log_to_all(logging.ERROR, error_msg)

    def result_data(self, data: dict[str, Any]) -> None:
        """Log structured result data."""
        formatted = self.formatter.format_data(data)
        self._log_to_all(logging.INFO, f"Result Data: {formatted}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit with cleanup."""
        self.cleanup()
        
    def get(self, name: str) -> BaseLogger | None:
        """Get a specific logger by name."""
        return self.loggers.get(name)

    def __repr__(self) -> str:
        """String representation."""
        enabled = [name for name, _ in self.loggers.items()]
        return (
            f"UnifiedLogger(enabled={enabled}, "
            f"level={logging.getLevelName(self.config.log_level)})"
        )