#!/usr/bin/env python
from .config import LoggerConfig
from .setup_loggers import setup_loggers
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
                
async def get_logger(webhook_url: str, loggers: set[str] = None):
    """Factory function to get configured logger instance."""
    logger_manager = AsyncLogger(loggers or {"local", "discord", "asio"})
    
    try:
        logger = await logger_manager.initialize(webhook_url)
        return logger, logger_manager
    except Exception as e:
        logging.error(f"Logger initialization failed: {e}")
        return None, None