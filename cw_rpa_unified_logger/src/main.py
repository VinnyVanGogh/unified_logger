
from cw_rpa_unified_logger.src import setup_loggers, LoggerConfig
import asyncio
    
async def cleanup_loggers(logger):
    discord_logger = logger.loggers.get("discord")
    if discord_logger:
        await discord_logger.cleanup()
    
async def main():
    loggers = "local,discord,asio"
    config = LoggerConfig(
        discord_webhook_url="https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz"
    )
    
    logger = setup_loggers(loggers, config)
    
    logger.update_config(
        max_message_length=2000,
        filter_patterns=["error", "warning"]
    )
    
    config = logger.config
    
    for k, v in config.__dict__.items():
      logger.info(f"{k}: {v}")
    
    await cleanup_loggers(logger)

  
if __name__ == "__main__":
    asyncio.run(main())