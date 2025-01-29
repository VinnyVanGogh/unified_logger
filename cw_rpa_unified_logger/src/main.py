#!/usr/bin/env python
# ./cw_rpa_unified_logger/src/main.py

from cw_rpa_unified_logger.src.loggers.async_logger import get_logger, AsyncLogger
import asyncio
import logging

# Replace with your Discord webhook URL or set to None if not using Discord logging
DISCORD_WEBHOOK = None  # e.g., "https://discord.com/api/webhooks/..."

async def cleanup_loggers(manager: AsyncLogger):
    """Cleanup loggers using the manager."""
    if manager:
        await manager.cleanup()

def log_examples(logger: logging.Logger):
    """
    Demonstrates logging at various levels.
    """
    logger.debug("Debug level information")
    logger.info("Info level information")
    logger.warning("Warning level alert")
    logger.error("Error level notification")
    logger.critical("Critical level issue")

async def main():
    """Initialize and demonstrate unified logger functionality."""
    logger_types = {"local", "discord", "asio"} if DISCORD_WEBHOOK else {"local", "asio"}

    logger, manager = await get_logger(
        webhook_url=DISCORD_WEBHOOK,
        log_level=logging.INFO,  # Set to DEBUG to capture debug logs
        logger_types=logger_types,
        enable_terminal=True,
        terminal_level=logging.WARNING
    )
    
    if logger:
        try:
            logger.info("Logger initialized successfully")
            logger.debug(f"Logger configuration: {manager.config.as_dict()}")
            log_examples(logger)
        finally:
            await cleanup_loggers(manager)
    else:
        logging.error("Failed to initialize logger")

if __name__ == "__main__":
    asyncio.run(main())
