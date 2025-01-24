#!/usr/bin/env python
from cw_rpa_unified_logger.src.loggers import get_logger
import asyncio

async def test():
  logger, manager = await get_logger(
      webhook_url="https://discord.com/api/webhooks/1332028030289186908/K1y0oexKLumsr6yGsnph4ww3PzPMoo8abpvyo8NPNziMWzI68P7_lmvbiKer2gkSSc-1",
      loggers={"local", "discord"}  # Specify only needed loggers
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