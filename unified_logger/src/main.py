
from dis import disco
from logging import config
from src import setup_loggers
import asyncio
    
async def cleanup(logger):
    discord_logger = logger.loggers.get("discord")
    if discord_logger:
        await discord_logger.cleanup()
    
async def main():
    loggers = "local,discord,asio"
    loggers = set(loggers.split(","))
    
    logger = setup_loggers(loggers)
    
    logger.update_config(
        max_message_length=2000,
        filter_patterns=["error", "warning"]
    )
    
    config = logger.config
    
    for k, v in config.__dict__.items():
      logger.info(f"{k}: {v}")
    
    await cleanup(logger)

  
if __name__ == "__main__":
    asyncio.run(main())