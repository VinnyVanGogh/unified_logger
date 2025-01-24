
from cw_rpa_unified_logger.src import get_logger
import asyncio
    
async def cleanup_loggers(logger):
    discord_logger = logger.loggers.get("discord")
    if discord_logger:
        await discord_logger.cleanup()
    
async def main():
    logger, logger_manager = await get_logger(
        webhook_url="https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz",
        loggers="discord,local"
    )
    if not logger:
        print("Failed to initialize logger")
        return

    try:
        # Use the logger
        logger.info("System initialized")
        logger.debug("Debug information")
        logger.warning("Warning message")
        
        # Get configuration from the active logger instance
        current_loggers = logger.config.current_loggers()
        logger_config = logger.config.as_dict()
        
        logger.info(f"Current loggers: {current_loggers}")
        logger.info(f"Logger configuration: {logger_config}")
        
    finally:
        await logger_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())