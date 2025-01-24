#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/local_logger.py

import logging
import json
import colorlog
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from cw_rpa_unified_logger.src.loggers.base import BaseLogger
from cw_rpa_unified_logger.src.loggers.config import LoggerConfig
from cw_rpa_unified_logger.src.loggers.types import LoggerType

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
        
        # Set up handlers
        self._setup_console_handler()
        if LoggerType.LOCAL in self.config.enabled_loggers:
            self._setup_file_handler()
            
    def _setup_console_handler(self) -> None:
        """Configure console handler with color support."""
        handler = colorlog.StreamHandler()
        handler.setLevel(self.config.log_level)
        
        formatter = colorlog.ColoredFormatter(
            '%(asctime)s - [%(process)d] - %(log_color)s%(levelname)s%(reset)s - '
            '%(log_color)s%(message)s%(reset)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            reset=True,
            style='%'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def _setup_file_handler(self) -> None:
        """Configure file handler with rotation support."""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        file_path = log_dir / self.config.log_file_name
        handler = logging.FileHandler(file_path, mode='w')
        handler.setLevel(self.config.log_level)
        
        formatter = logging.Formatter(
            '%(asctime)s - [%(process)d] - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Write initial log entry
        with open(file_path, 'w') as f:
            f.write(f"Log started at {datetime.now(UTC)} "
                   f"with config: {self.config}\n")

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