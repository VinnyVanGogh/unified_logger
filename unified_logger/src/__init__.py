from src.loggers import UnifiedLogger, LoggerConfig, LoggerType, setup_loggers

def setup_loggers(types: set[LoggerType]) -> UnifiedLogger:
    # Initialize with specific loggers
    valid_types = {
        "local": LoggerType.LOCAL,
        "discord": LoggerType.DISCORD,
        "asio": LoggerType.ASIO
    }
    enabled_loggers = {valid_types[t] for t in types if t in valid_types}
    
    config = LoggerConfig(
        enabled_loggers=enabled_loggers,
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