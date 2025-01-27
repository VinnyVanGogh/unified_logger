#!/usr/bin/env python
from .config import LoggerConfig
from .setup_loggers import setup_loggers
from .unified import UnifiedLogger
from .types import LoggerType
from typing import Optional, Set, Tuple, Union, List
import logging
import asyncio

class AsyncLogger:
    def __init__(self, logger_types: set[str], log_level: int = logging.INFO):
        self.logger = None
        self.config = None
        # Convert set/list to comma-separated string
        if isinstance(logger_types, (set, list)):
            # Convert each type to string and ensure they're valid
            valid_types = LoggerType.get_valid_types()
            logger_types = {t for t in logger_types if t in valid_types}
            logger_types = ",".join(logger_types)
            
        self.enabled_loggers = LoggerType.from_input(logger_types)
        
        self.log_level = log_level

        # Store raw input for later use in initialize
        self.raw_logger_types = self.enabled_loggers

    async def initialize(self, webhook_url: str, log_level: int = logging.INFO) -> Optional[UnifiedLogger]:
        """Initialize logger with configuration and types."""
        try:
            config = LoggerConfig(
                discord_webhook_url=webhook_url,
                max_message_length=2000,
                filter_patterns=["error", "warning"],
                log_level=log_level
            )
            
            # Initialize logger with both types and config
            self.logger = setup_loggers(
                types=self.raw_logger_types,  # Pass raw types to setup_loggers
                config=config
            )
            self.config = config
            return self.logger
            
        except Exception as e:
            logging.error(f"Logger initialization failed: {e}")
            return None
            
        except Exception as e:
            logging.error(f"Logger initialization failed: {e}")
            return None

    async def cleanup(self):
        """Ensure proper cleanup and message sending."""
        if self.logger and hasattr(self.logger, 'loggers'):
            discord_logger = self.logger.loggers.get("discord")
            if discord_logger:
                print("Cleaning up Discord logger...")
                # Force process any remaining messages
                await discord_logger.cleanup()
                # Give time for messages to process
                await asyncio.sleep(1)
                
async def get_logger(
    webhook_url: str, 
    log_level: int = logging.INFO,
    logger_types: Union[str, Set[str], List[str], None] = None
) -> Tuple[Optional[UnifiedLogger], Optional[AsyncLogger]]:
    """Initialize configured logger instance."""
    try:
        print(f"Logger types: {logger_types} with types: {type(logger_types)}")
        print(f"Log level: {log_level} with type: {type(log_level)}")
        logger_manager = AsyncLogger(logger_types, log_level)  # Pass raw input
        logger = await logger_manager.initialize(webhook_url)
        
        if logger:
            logging.debug(f"Initialized loggers: {logger.config.current_loggers()}")
            return logger, logger_manager
            
    except Exception as e:
        logging.error(f"Logger initialization failed: {str(e)}")
        return None, None