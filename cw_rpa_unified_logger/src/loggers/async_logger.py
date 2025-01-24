#!/usr/bin/env python
from .config import LoggerConfig
from .setup_loggers import setup_loggers
from .unified import UnifiedLogger
from typing import Optional, Set, Tuple
import logging

class AsyncLogger:
    def __init__(self, loggers: set[str]):
        self.logger = None
        self.config = None
        self.loggers = {}

    async def initialize(self, webhook_url: str):
        """Initialize the logger with configuration."""
        if not self.loggers:
          loggers = "local,discord,asio"
        else:
          loggers = self.loggers
        config = LoggerConfig(
            discord_webhook_url=webhook_url,
            max_message_length=2000,
            filter_patterns=["error", "warning"],
            log_level=logging.INFO
        )
        
        self.logger = setup_loggers(loggers, config)
        self.config = self.logger.config
        return self.logger

    async def cleanup(self):
        """Cleanup logger resources."""
        if self.logger:
            discord_logger = self.logger.loggers.get("discord")
            if discord_logger:
                await discord_logger.cleanup()
                
async def get_logger(
    webhook_url: str, 
    loggers: Optional[Set[str]] = None
) -> Tuple[Optional[UnifiedLogger], Optional[AsyncLogger]]:
    """
    Factory function to get configured logger instance.
    
    Args:
        webhook_url: Discord webhook URL for notifications
        loggers: Set of logger types to enable. Defaults to all loggers.
        
    Returns:
        Tuple containing:
        - UnifiedLogger instance or None if initialization fails
        - AsyncLogger manager instance or None if initialization fails
        
    Example:
        >>> logger, manager = await get_logger(
        ...     webhook_url="https://discord.com/api/webhooks/...",
        ...     loggers={"local", "discord"}
        ... )
    """
    try:
        # Default to all available loggers if none specified
        enabled_loggers = loggers or {"local", "discord", "asio"}
        
        # Validate logger types
        valid_types = {"local", "discord", "asio"}
        invalid_loggers = enabled_loggers - valid_types
        if invalid_loggers:
            raise ValueError(f"Invalid logger types: {invalid_loggers}")
        
        # Initialize logger manager
        logger_manager = AsyncLogger(enabled_loggers)
        logger = await logger_manager.initialize(webhook_url)
        
        return logger, logger_manager
        
    except Exception as e:
        logging.error(f"Logger initialization failed: {str(e)}")
        return None, None