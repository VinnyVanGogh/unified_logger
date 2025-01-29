#!/usr/bin/env python
# ./cw_rpa_unified_logger/src/loggers/async_logger.py
from .config import LoggerConfig
from .unified import UnifiedLogger
from .types import LoggerType
from .handlers import LogHandlerFactory
from typing import Optional, Set, Tuple, Union, List
import logging
import asyncio

class AsyncLogger:
    def __init__(self, config: LoggerConfig):
        self.logger = None
        self.config = config
        self.enabled_loggers = config.enabled_loggers
        self.log_level = config.log_level
        self.raw_logger_types = self.enabled_loggers

    async def initialize(self) -> Optional[UnifiedLogger]:
        """Initialize logger with configuration and types."""
        try:
            # Initialize base logger
            self.logger = UnifiedLogger(self.config)
            
            await self.logger._initialize()
            
            # Set up handlers using factory
            handlers = LogHandlerFactory.create_handlers(
                level=self.config.log_level,
                log_file=self.config.log_dir / self.config.log_file_name,
                enable_console=self.config.enable_terminal_output,
                terminal_level=self.config.terminal_level
            )
            
            # Add handlers to root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(self.log_level)  # Ensure root captures all levels
            for handler in handlers:
                if handler not in root_logger.handlers:
                    root_logger.addHandler(handler)
            
            # If UnifiedLogger has its own logger, attach it to root
            if hasattr(self.logger, 'logger'):
                unified_logger = self.logger.logger
                unified_logger.setLevel(self.config.log_level)
                if unified_logger not in root_logger.handlers:
                    root_logger.addHandler(unified_logger)
            
            # Initialize specialized loggers
            await self._initialize_specialized_loggers()
            
            return self.logger

        except Exception as e:
            logging.error(f"Logger initialization failed: {e}")
            return None


    async def _initialize_specialized_loggers(self):
        """Initialize Discord and other specialized loggers."""
        if not self.logger or not hasattr(self.logger, 'loggers'):
            return

        for logger_name, logger_instance in self.logger.loggers.items():
            if logger_name == "discord" and hasattr(logger_instance, 'initialize'):
                await logger_instance.initialize()

    async def cleanup(self):
        """Ensure proper cleanup of all loggers."""
        if self.logger and hasattr(self.logger, 'loggers'):
            # Clean up specialized loggers
            for logger_name, logger_instance in self.logger.loggers.items():
                try:
                    if logger_name == "discord":
                        await logger_instance.cleanup()
                        await asyncio.sleep(1)
                    elif hasattr(logger_instance, 'cleanup'):
                        logger_instance.cleanup()
                except Exception as e:
                    logging.error(f"Error cleaning up {logger_name} logger: {e}")

            # Clean up handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)

                
async def get_logger(
    webhook_url: str, 
    log_level: int = logging.INFO,
    logger_types: Union[str, Set[str], List[str], None] = None,
    enable_terminal: bool = False,  # Add control for terminal output
    terminal_level: int = logging.WARNING  # Set terminal level
) -> Tuple[Optional[UnifiedLogger], Optional[AsyncLogger]]:
    """Initialize configured logger instance with async support."""
    logger_manager = None
    try:
        # Disable root logger handlers to prevent duplication
        logging.getLogger().handlers = []
        
        # Create LoggerConfig instance
        config = LoggerConfig(
            discord_webhook_url=webhook_url,
            max_message_length=2000,
            filter_patterns=["error", "warning"],
            log_level=log_level,
            enable_terminal_output=enable_terminal,
            terminal_level=terminal_level,
            enabled_loggers=logger_types
        )
        
        # Initialize logger manager with the config
        logger_manager = AsyncLogger(config)
        
        # Initialize the logger
        logger = await logger_manager.initialize()
        
        if logger:
            logger.debug(f"Initialized loggers: {logger.config}")
            return logger, logger_manager
                
    except Exception as e:
        logging.error(f"Logger initialization failed: {str(e)}", exc_info=True)
        if logger_manager:
            await logger_manager.cleanup()
        return None, None