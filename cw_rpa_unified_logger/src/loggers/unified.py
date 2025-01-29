#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/unified.py

import logging
from contextlib import contextmanager
import functools
from typing import Any, Generator, Callable
from collections.abc import Callable
import asyncio

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
            
        
    async def _initialize(self) -> None:
        """Async initialization for loggers."""
        try:
            if LoggerType.LOCAL in self.config.enabled_loggers:
                self.loggers["local"] = LocalLogger(self.config)
            if LoggerType.ASIO in self.config.enabled_loggers:
                self.loggers["asio"] = AsioLogger()
            if LoggerType.DISCORD in self.config.enabled_loggers:
                discord_logger = DiscordLogger(
                    self.config.discord_webhook_url,
                    self.config.logger_name
                )
                await discord_logger.initialize()  # Await async setup
                self.loggers["discord"] = discord_logger
        except Exception as e:
            logging.error(f"Failed to initialize loggers: {e}")

    def _format_exception(self, exc_info: tuple) -> str:
        """Format exception info into a readable string."""
        import traceback
        return ''.join(traceback.format_exception(*exc_info))
    
    async def update_config(self, **kwargs) -> None:
        """
        Update logger configuration dynamically.
        
        Args:
            **kwargs: Configuration overrides
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                
        await self._initialize()
            
    def _log_to_all(self, level: int, message: str, exc_info: bool | tuple | None = None) -> None:
        """
        Distribute log message to all active backends with exception handling.
        """
        processed = self.formatter.process_message(message)
        if processed is None:
            return

        # Handle exception info
        if exc_info:
            if exc_info is True:
                import sys
                exc_info = sys.exc_info()
            if isinstance(exc_info, tuple) and len(exc_info) == 3:
                processed = f"{processed}\n{self._format_exception(exc_info)}"

        for name, logger in self.loggers.items():
            try:
                logger.log(level, processed)
            except Exception as e:
                print(f"Logging failed for {name}: {e}")



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

    # Update logging methods to handle exc_info
    def debug(self, message: str, exc_info: bool | tuple | None = None) -> None:
        self._log_to_all(logging.DEBUG, message, exc_info)

    def info(self, message: str, exc_info: bool | tuple | None = None) -> None:
        self._log_to_all(logging.INFO, message, exc_info)

    def warning(self, message: str, exc_info: bool | tuple | None = None) -> None:
        self._log_to_all(logging.WARNING, message, exc_info)

    def error(self, message: str, exc_info: bool | tuple | None = None) -> None:
        self._log_to_all(logging.ERROR, message, exc_info)

    def critical(self, message: str, exc_info: bool | tuple | None = None) -> None:
        self._log_to_all(logging.CRITICAL, message, exc_info)

    def exception(self, e: Exception, message: str = "") -> None:
        """Log exception with full traceback."""
        import sys
        error_msg = f"{message + ': ' if message else ''}{str(e)}"
        self._log_to_all(logging.ERROR, error_msg, sys.exc_info())

    def result_data(self, data: dict[str, Any]) -> None:
        """Log structured result data."""
        formatted = self.formatter.format_data(data)
        self._log_to_all(logging.INFO, f"Result Data: {formatted}")
        if LoggerType.ASIO in self.config.enabled_loggers:
            AsioLogger().result_data(data)
            
    def result_failed_message(self, message: str) -> None:
        """Log a failed message result."""
        if LoggerType.ASIO in self.config.enabled_loggers:
            AsioLogger().result_failed_message(message)

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