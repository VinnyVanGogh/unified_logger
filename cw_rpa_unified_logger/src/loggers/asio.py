#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/asio_logger.py

import logging
from typing import Any
from cw_rpa import Logger as AsioLoggerBase
from cw_rpa_unified_logger.src.loggers.base import BaseLogger

class AsioLogger(BaseLogger):
    """
    Asio logging implementation supporting remote logging integration.
    Handles connection management and graceful fallback on failures.
    """
    
    def __init__(self):
        """Initialize Asio logger with error handling."""
        try:
            self.logger = AsioLoggerBase()
            self._connected = True
        except ImportError as e:
            self._connected = False
            logging.error(f"Failed to initialize Asio logger: {e}")
            
    def _safe_log(self, method: str, message: str) -> None:
        """
        Safely execute Asio logging operations with fallback.
        
        Args:
            method (str): Logging method name to call
            message (str): Message to log
        """
        if not self._connected:
            return
            
        try:
            log_method = getattr(self.logger, method, None)
            if log_method:
                log_method(message)
        except Exception as e:
            logging.error(f"Asio logging failed ({method}): {e}")
            self._connected = False  # Mark as disconnected on failure

    def log(self, level: int, message: str) -> None:
        """Log a message at the specified level."""
        level_name = logging.getLevelName(level).lower()
        self._safe_log(level_name, message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._safe_log('debug', message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._safe_log('info', message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._safe_log('warning', message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._safe_log('error', message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._safe_log('critical', message)
        
    def exception(self, e: Exception, message: str) -> None:
        """Log an exception with additional context."""
        error_msg = f"{message}: {str(e)}"
        self._safe_log('error', error_msg)
        
    def result_data(self, data: dict[str, Any]) -> None:
        """Log structured result data."""
        try:
            if self._connected:
                self.logger.result_data(data)
        except Exception as e:
            logging.error(f"Failed to log result data to Asio: {e}")
            self._connected = False

    def cleanup(self) -> None:
        """Clean up Asio logger resources."""
        if hasattr(self, 'logger') and hasattr(self.logger, 'cleanup'):
            try:
                self.logger.cleanup()
            except Exception as e:
                logging.error(f"Error cleaning up Asio logger: {e}")