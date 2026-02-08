#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/local_logger.py

import logging
import json
from typing import Any

from cw_rpa_unified_logger.src.loggers.handlers import LogHandlerFactory
from cw_rpa_unified_logger.src.loggers.base import BaseLogger
from cw_rpa_unified_logger.src.loggers.config import LoggerConfig

class LocalLogger(BaseLogger):
    """
    Local logging implementation supporting both console and file output
    with colored console formatting and structured file logging.
    """
    
    def __init__(self, config: LoggerConfig):
        """
        Initialize local logger with configuration.
        
        Args:
            config (LoggerConfig): Logger configuration
        """
        self.config = config
        self.logger = logging.getLogger(config.logger_name or __name__)
        self.logger.setLevel(config.log_level)
        self.logger.handlers = []  # Clear existing handlers
        self.setup_handlers()
        
    def setup_handlers(self) -> None:
        handler_factory = LogHandlerFactory()
        handlers = handler_factory.create_handlers(
            level=self.config.log_level,
            log_file=self.config.log_dir / self.config.log_file_name,
            enable_console=self.config.enable_terminal_output
        )
        for handler in handlers:
            self.logger.addHandler(handler)

    def log(self, level: int, message: str) -> None:
        """Log a message at the specified level."""
        self.logger.log(level, message)
        
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)
        
    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
        
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
        
    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)
        
    def critical(self, message: str) -> None:
        """Log a critical message."""
        self.logger.critical(message)
        
    def exception(self, e: Exception, message: str) -> None:
        """Log an exception with additional context."""
        error_msg = f"{message}: {str(e)}"
        self.logger.error(error_msg)
        
    def result_data(self, data: dict[str, Any]) -> None:
        """Log structured result data."""
        try:
            formatted_data = json.dumps(data, indent=2, default=str)
            self.logger.info(f"Result Data: {formatted_data}")
        except (TypeError, ValueError) as e:
            self.logger.error(f"Failed to format result data: {e}")
            self.logger.info(f"Result Data: {str(data)}")
            
    def cleanup(self) -> None:
        """Clean up logger resources."""
        for handler in self.logger.handlers[:]:
            try:
                handler.close()
                self.logger.removeHandler(handler)
            except Exception as e:
                print(f"Error closing handler: {e}")