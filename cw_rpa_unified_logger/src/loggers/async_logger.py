#!/usr/bin/env python
from .config import LoggerConfig
from .setup_loggers import setup_loggers
from .unified import UnifiedLogger
from .types import LoggerType
from typing import Optional, Set, Tuple, Union, List
import logging

class AsyncLogger:
    def __init__(self, logger_types: set[str]):
        self.logger = None
        self.config = None
        # Convert set/list to comma-separated string
        if isinstance(logger_types, (set, list)):
            # Convert each type to string and ensure they're valid
            valid_types = LoggerType.get_valid_types()
            logger_types = {t for t in logger_types if t in valid_types}
            logger_types = ",".join(logger_types)
            
        self.enabled_loggers = LoggerType.from_input(logger_types)


    async def initialize(self, webhook_url: str):
        """
        Initialize the logger with configuration and proper type handling.
        
        Args:
            webhook_url: Discord webhook URL for notifications
            
        Returns:
            UnifiedLogger: Configured logger instance
        """
        try:
            config = LoggerConfig(
                enabled_loggers=self.enabled_loggers,
                discord_webhook_url=webhook_url,
                max_message_length=2000,
                filter_patterns=["error", "warning"],
                log_level=logging.INFO
            )
            
            # Pass both config and logger types for proper initialization
            self.logger = setup_loggers(
                types=self.enabled_loggers,  # Already converted to LoggerType set
                config=config
            )
            self.config = self.logger.config
            return self.logger
            
        except Exception as e:
            logging.error(f"Logger initialization failed: {e}")
            return None

    async def cleanup(self):
        """Cleanup logger resources."""
        if self.logger and hasattr(self.logger, 'loggers'):
            discord_logger = self.logger.loggers.get("discord")
            if discord_logger:
                await discord_logger.cleanup()
                
async def get_logger(
    webhook_url: str, 
    logger_types: Union[str, Set[str], List[str], None] = None
) -> Tuple[Optional[UnifiedLogger], Optional[AsyncLogger]]:
    """Initialize configured logger instance."""
    try:
        print(f"Logger types: {logger_types} with types: {type(logger_types)}")
        logger_manager = AsyncLogger(logger_types)  # Pass raw input
        logger = await logger_manager.initialize(webhook_url)
        
        if logger:
            logging.debug(f"Initialized loggers: {logger.config.current_loggers()}")
            return logger, logger_manager
            
    except Exception as e:
        logging.error(f"Logger initialization failed: {str(e)}")
        return None, None