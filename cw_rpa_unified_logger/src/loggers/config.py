#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/config.py

from dataclasses import dataclass, field
from typing import Optional, Set
import logging
from pathlib import Path
from cw_rpa_unified_logger.src.loggers.types import LoggerType
from cw_rpa_unified_logger.src.loggers.handlers import LogHandlerFactory

@dataclass
class LoggerConfig:
    """Configuration settings for the unified logging system."""
    # Logger enablement flags
    enabled_loggers: Set[LoggerType] = field(
        default_factory=lambda: {LoggerType.LOCAL},
        metadata={"converter": lambda x: set(x) if isinstance(x, (list, tuple, set)) else {x}}
    )
    
    # Core settings
    logger_name: str = "unified_logger"
    log_level: int = logging.INFO
    max_message_length: int = 10000
    
    # Terminal output control
    terminal_level: int = logging.WARNING  # Only show WARNING and above in terminal
    enable_terminal_output: bool = False
    
    # Local logging settings
    log_dir: Path = field(default_factory=lambda: Path(__file__).parent / "logs")
    log_file_name: str = "app.log"
    
    # External service settings
    discord_webhook_url: Optional[str] = None
    asio_config: Optional[dict] = None
    
    # Message processing
    filter_patterns: list[str] = field(default_factory=list)
    enable_debug_mode: bool = False

    def __post_init__(self):
        """Ensure enabled_loggers is a set of valid LoggerType values."""
        try:
            self.enabled_loggers = LoggerType.from_input(self.enabled_loggers)
        except KeyError as e:
            raise ValueError(f"Invalid logger type: {e}")
        
        if not self.enabled_loggers:
            raise ValueError("At least one logger must be enabled")

        self._validate_config()
      
    def get_handlers(self) -> list:
        """Get configured logging handlers based on settings using LogHandlerFactory."""
        return LogHandlerFactory.create_handlers(
            level=self.log_level,
            log_file=self.log_dir / self.log_file_name if LoggerType.LOCAL in self.enabled_loggers else None,
            enable_console=self.enable_terminal_output
        )
        
    def _validate_config(self) -> None:
        """
        Validate configuration settings.
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate logger types
        if not self.enabled_loggers:
            raise ValueError("At least one logger must be enabled")
        if not any(logger in self.enabled_loggers for logger in LoggerType.all_types()):
            raise ValueError("Invalid logger type specified")
        
        # Validate log level
        valid_levels = {
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL
        }
        if self.log_level not in valid_levels:
            raise ValueError(
                f"Invalid log level: {self.log_level}. "
                f"Must be one of: {[logging.getLevelName(l) for l in valid_levels]}"
            )
            
        # Validate terminal level
        if self.terminal_level not in valid_levels:
            raise ValueError(
                f"Invalid terminal log level: {self.terminal_level}. "
                f"Must be one of: {[logging.getLevelName(l) for l in valid_levels]}"
            )
        
        # Ensure terminal level is not lower than overall log level
        if self.enable_terminal_output and self.terminal_level < self.log_level:
            self.terminal_level = self.log_level
            
        # Validate message length
        if self.max_message_length <= 0:
            raise ValueError("max_message_length must be positive")
            
        # Validate Discord config
        if LoggerType.DISCORD in self.enabled_loggers and not self.discord_webhook_url:
            raise ValueError("Discord logging enabled but no webhook URL provided")
          
        if LoggerType.LOCAL in self.enabled_loggers and not self.log_dir:
            raise ValueError("Local logging enabled but no log directory provided")
          
        if LoggerType.LOCAL in self.enabled_loggers and not self.log_file_name:
            raise ValueError("Local logging enabled but no log file name provided")
          
            
        # Validate filter patterns
        for pattern in self.filter_patterns:
            try:
                import re
                re.compile(pattern)
            except re.error as e:
                raise ValueError(f"Invalid filter pattern '{pattern}': {e}")
          
    def should_log_to_terminal(self, level: int) -> bool:
        """Determine if a message should be logged to terminal."""
        return (
            self.enable_terminal_output and 
            level >= self.terminal_level
        )
              
    def update(self, **kwargs) -> None:
        """
        Update configuration with validation.
        
        Args:
            **kwargs: Configuration attributes to update
            
        Raises:
            ValueError: If invalid configuration provided
        """
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Invalid configuration attribute: {key}")
            setattr(self, key, value)
        self._validate_config()
        
    def as_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            key: str(value) if isinstance(value, Path) else value
            for key, value in self.__dict__.items()
        }
        
    def current_loggers(self) -> set[str]:
        """Get currently enabled loggers as a set of strings."""
        return {logger.name for logger in self.enabled_loggers}
        
    def __str__(self) -> str:
        """String representation of configuration."""
        return (
            f"LoggerConfig("
            f"enabled_loggers={self.enabled_loggers}, "
            f"log_level={self.log_level} ({logging.getLevelName(self.log_level)}), "
            f"max_message_length={self.max_message_length}, "
            f"log_dir={self.log_dir}, "
            f"log_file_name={self.log_file_name}, "
            f"discord_webhook_url={self.discord_webhook_url}, "
            f"asio_config={self.asio_config}, "
            f"filter_patterns={self.filter_patterns}, "
            f"enable_debug_mode={self.enable_debug_mode}, "
            f"enable_terminal_output={self.enable_terminal_output}, "
            f"terminal_level={self.terminal_level} ({logging.getLevelName(self.terminal_level)})"
            f")"
        )

