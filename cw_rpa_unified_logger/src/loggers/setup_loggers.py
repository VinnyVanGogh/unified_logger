#!/usr/bin/env python
from .types import LoggerType
from .config import LoggerConfig
from .unified import UnifiedLogger
from typing import Union

def setup_loggers(types: Union[str, set], config: LoggerConfig) -> UnifiedLogger:
    """
    Initialize loggers based on the provided types and configuration.
    
    Args:
        types: Logger types as comma-separated string or set
        config: LoggerConfig instance with initial settings
        
    Returns:
        UnifiedLogger: Configured logger instance
    """
    # Convert string input to set if needed
    if isinstance(types, str):
        type_set = set(types.split(','))
    else:
        type_set = types

    # Map string types to LoggerType enum
    valid_types = {
        "local": LoggerType.LOCAL,
        "discord": LoggerType.DISCORD,
        "asio": LoggerType.ASIO
    }
    
    enabled_loggers = {
        valid_types[t.strip().lower()] 
        for t in type_set 
        if t.strip().lower() in valid_types
    }
    
    # Update config with enabled loggers
    config.enabled_loggers = enabled_loggers
    
    # Initialize logger directly with the updated config
    logger = UnifiedLogger(config)
    
    return logger