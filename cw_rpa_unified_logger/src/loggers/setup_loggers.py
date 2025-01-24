#!/usr/bin/env python
from .types import LoggerType
from .config import LoggerConfig
from .unified import UnifiedLogger
from typing import Union

def setup_loggers(types: Union[str, set, LoggerType], config: LoggerConfig) -> UnifiedLogger:
    """
    Initialize loggers based on the provided types and configuration.
    
    Args:
        types: Logger types as LoggerType set, comma-separated string, or set of strings
        config: LoggerConfig instance with initial settings
        
    Returns:
        UnifiedLogger: Configured logger instance
    """
    # If already a set of LoggerTypes, use directly
    if isinstance(types, set) and all(isinstance(t, LoggerType) for t in types):
        enabled_loggers = types
    else:
        # Use the from_input method for consistent conversion
        enabled_loggers = LoggerType.from_input(types)
    
    # Update config with enabled loggers
    config.enabled_loggers = enabled_loggers
    
    # Initialize and return logger
    return UnifiedLogger(config)