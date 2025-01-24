#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/config.py

from dataclasses import dataclass, field
from typing import Optional, Set
import logging
from pathlib import Path
from cw_rpa_unified_logger.src.loggers.types import LoggerType

@dataclass
class LoggerConfig:
    """
    Configuration settings for the unified logging system.
    Provides type-safe configuration with validation.
    """
    # Logger enablement flags
    enabled_loggers: Set[LoggerType] = field(
        default_factory=lambda: {LoggerType.LOCAL},
        metadata={"converter": lambda x: set(x) if isinstance(x, (list, tuple, set)) else {x}}
    )
    
    # Core settings
    logger_name: str = "unified_logger"
    log_level: int = logging.INFO
    max_message_length: int = 10000
    
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
        if not isinstance(self.enabled_loggers, set):
            try:
                # Handle string input (e.g., "local,discord")
                if isinstance(self.enabled_loggers, str):
                    logger_names = self.enabled_loggers.split(',')
                    self.enabled_loggers = {
                        LoggerType[name.strip().upper()]
                        for name in logger_names
                    }
                else:
                    self.enabled_loggers = set(self.enabled_loggers)
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid logger types: {e}")

        # Validate all elements are LoggerType
        for logger in self.enabled_loggers:
            if not isinstance(logger, LoggerType):
                raise ValueError(f"Invalid logger type: {logger}")

        self._validate_config()
        
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
            f"log_level={self.log_level}, "
            f"log_dir={self.log_dir}, "
            f"log_file_name={self.log_file_name}, "
            f"discord_webhook_url={self.discord_webhook_url}, "
            f"level={logging.getLevelName(self.log_level)})"
        )