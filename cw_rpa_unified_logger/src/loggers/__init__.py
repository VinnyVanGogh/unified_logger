"""
This module provides a unified interface for different logging backends, allowing you to log in multiple formats and to multiple destinations at once.
"""

from .unified import UnifiedLogger
from .config import LoggerConfig
from .types import LoggerType

def setup_loggers(types: set[LoggerType], new_config: LoggerConfig) -> UnifiedLogger:
    """
    Initialize loggers based on the provided types.
    """
    # Initialize with specific loggers
    valid_types = {
        "local": LoggerType.LOCAL,
        "discord": LoggerType.DISCORD,
        "asio": LoggerType.ASIO
    }
    enabled_loggers = {valid_types[t] for t in types if t in valid_types}
    
    print(new_config)
    
    for k, v in new_config.__dict__.items():
        print(f"{k}: {v}")
        
    new_config.enabled_loggers = enabled_loggers
    
    config = LoggerConfig(
        **new_config.as_dict()
    )

    # Initialize unified logger
    logger = UnifiedLogger(config)

    # Log messages
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    return logger

__all__ = [
    "UnifiedLogger",
    "LoggerConfig",
    "LoggerType",
    "setup_loggers"
]