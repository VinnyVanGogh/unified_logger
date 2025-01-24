#!/usr/bin/env python
from cw_rpa_unified_logger.src.main import main
from cw_rpa_unified_logger.src.loggers import get_logger
import asyncio

async def test():
  logger, manager = await get_logger(
      webhook_url="https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz",
      logger_types={"local", "discord"}  # Specify only needed loggers
  )
  if logger:
      try:
          logger.info("System initialized")
          # Your code here
      finally:
          await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test())
    # asyncio.run(main())