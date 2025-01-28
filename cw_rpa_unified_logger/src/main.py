#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./cw_rpa_unified_logger/src/main.py
from cw_rpa_unified_logger.src import get_logger
import asyncio
import logging
    
DISCORD_WEBHOOK = None  # Replace with your Discord webhook URL
    
async def cleanup_loggers(logger):
    discord_logger = logger.loggers.get("discord")
    if discord_logger:
        await discord_logger.cleanup()
    
def log_examples(logger: logging.Logger):
    """
    Demonstrates logging at various levels.
    """
    logger.debug("Debug level information")
    logger.warning("Warning level alert")
    logger.error("Error level notification")
    
async def main():
    """
    Initialize and demonstrate unified logger functionality.
    
    Demonstrates logging at various levels and ensures proper cleanup.
    
    Available logger types:
    - "local": File-based logging
    - "discord": Discord webhook notifications 
    - "asio": ASIO system integration
    """
    logger, manager = await get_logger(
        webhook_url=DISCORD_WEBHOOK,
        logger_types={"local", "discord", "asio"}  # defaults to all three but you can remove as needed
    )
    
    if logger:
        try:
            # Example logging usage
            logger.info("Logger initialized successfully")
            
            log_examples(logger)
            
            
            # Your application code here
            
        finally:
            # Ensure proper cleanup of logger resources
            await manager.cleanup()
    else:
        logging.error("Failed to initialize logger")

if __name__ == "__main__":
   asyncio.run(main())