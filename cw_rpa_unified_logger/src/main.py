
from cw_rpa_unified_logger.src import get_logger
import asyncio
    
async def cleanup_loggers(logger):
    discord_logger = logger.loggers.get("discord")
    if discord_logger:
        await discord_logger.cleanup()
    
async def main():
    logger, logger_manager = await get_logger("webhook_url")
    if not logger:
        print("Failed to initialize logger")
        return

    try:
        # Use the logger
        logger.info("System initialized")
        logger.debug("Debug information")
        logger.warning("Warning message")
        
        # Your application logic here
        
    finally:
        # Cleanup
        await logger_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())