#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/discord.py

import logging
import json
import asyncio
import time
from datetime import datetime, UTC
from typing import Any
import aiohttp
from cw_rpa_unified_logger.src.loggers.base import BaseLogger

class DiscordLogger(BaseLogger):
    """
    Enhanced Discord webhook logging implementation supporting batching,
    rate limiting, and automatic retries.
    """
    
    # Discord-specific color mappings
    DEFAULT_COLORS = {
        logging.DEBUG: 0x7F7F7F,    # Gray
        logging.INFO: 0x3498DB,     # Blue
        logging.WARNING: 0xF1C40F,  # Yellow
        logging.ERROR: 0xE74C3C,    # Red
        logging.CRITICAL: 0x992D22  # Dark Red
    }
    
    def __init__(self, discord_webhook_url: str, logger_name: str = "Application Logger"):
        """
        Initialize Discord logger with webhook configuration.
        
        Args:
            discord_webhook_url (str): Discord webhook URL
            logger_name (str): Logger name for webhook messages
        """
        self.discord_webhook_url = discord_webhook_url
        self.username = logger_name
        self._session = None
        
        # Batching configuration
        self.message_queue = []
        self.last_batch_time = time.time()
        self.batch_size = 5          # Messages per batch
        self.batch_interval = 5      # Seconds between batches
        self.max_retries = 3         # Maximum retry attempts
        self.retry_delay = 1         # Seconds between retries
        self.max_embed_length = 1900 # Discord's limit is 2000, leave margin
        
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is initialized."""
        if self._session is None or self._session.closed:
            logging.debug("Initializing aiohttp.ClientSession.")
            self._session = aiohttp.ClientSession()
        elif self._session.closed:
            logging.warning("Reinitializing closed aiohttp.ClientSession.")
            self._session = aiohttp.ClientSession()



    def _truncate_message(self, message: str) -> str:
        """Safely truncate message to fit Discord's limits."""
        if len(message) > self.max_embed_length:
            return f"{message[:self.max_embed_length-3]}..."
        return message

    def _create_embed(self, level: int, message: str) -> dict:
        """Create a Discord embed for the message."""
        return {
            "title": f"{logging.getLevelName(level)} Log",
            "description": self._truncate_message(message),
            "color": self.DEFAULT_COLORS.get(level, 0x7F7F7F),
            "timestamp": datetime.now(UTC).isoformat()
        }

    async def _send_batch(self, retries: int = 0) -> bool:
        """Send accumulated messages as a batch with retry logic."""
        if not self.message_queue:
            return True

        try:
            await self._ensure_session()

            if self._session is None:
                raise RuntimeError("Client session not initialized.")

            logging.debug("Sending batch to Discord.")
            payload = {
                "username": self.username,
                "embeds": self.message_queue[:10]  # Discord limit
            }

            async with self._session.post(
                self.discord_webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 429:  # Rate limited
                    logging.warning("Rate limited, retrying...")
                    if retries < self.max_retries:
                        await asyncio.sleep(self.retry_delay)
                        return await self._send_batch(retries + 1)
                    return False

                if response.status in [502, 503, 504]:  # Gateway errors
                    logging.warning(f"Gateway error {response.status}, retrying...")
                    if retries < self.max_retries:
                        await asyncio.sleep(self.retry_delay * (retries + 1))
                        return await self._send_batch(retries + 1)

                await response.raise_for_status()
                self.message_queue = self.message_queue[10:]
                self.last_batch_time = time.time()
                return True

        except Exception as e:
            logging.error(f"Error sending batch: {e}")
            if retries < self.max_retries:
                await asyncio.sleep(self.retry_delay)
                await self._ensure_session()  # Ensure session before retrying
                return await self._send_batch(retries + 1)
            return False



    async def _process_message(self, level: int, message: str) -> None:
        """
        Process and queue a message for sending.
        
        Args:
            level (int): Logging level
            message (str): Message to log
        """
        try:
            embed = self._create_embed(level, message)
            self.message_queue.append(embed)
            
            current_time = time.time()
            should_send = (
                len(self.message_queue) >= self.batch_size or
                current_time - self.last_batch_time >= self.batch_interval
            )
            
            if should_send:
                await self._send_batch()
                
        except Exception as e:
            logging.error(f"Discord message processing failed: {e}")

    def _sync_log(self, level: int, message: str) -> None:
        """Synchronous wrapper for async logging."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create a new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Use create_task for already running loops
            asyncio.create_task(self._process_message(level, message))
        else:
            # Run the coroutine in a new loop
            loop.run_until_complete(self._process_message(level, message))



    def log(self, level: int, message: str) -> None:
        """Log a message at the specified level."""
        self._sync_log(level, message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._sync_log(logging.DEBUG, message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._sync_log(logging.INFO, message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._sync_log(logging.WARNING, message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._sync_log(logging.ERROR, message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._sync_log(logging.CRITICAL, message)

    def exception(self, e: Exception, message: str) -> None:
        """Log an exception with additional context."""
        error_msg = f"{message}: {str(e)}"
        self._sync_log(logging.ERROR, error_msg)

    def result_data(self, data: dict[str, Any]) -> None:
        """Log structured result data."""
        try:
            formatted_data = json.dumps(data, indent=2, default=str)
            self._sync_log(
                logging.INFO,
                f"Result Data:\n```json\n{formatted_data}\n```"
            )
        except Exception as e:
            logging.error(f"Failed to format result data for Discord: {e}")

    async def cleanup(self) -> None:
        """Clean up Discord logger resources and send remaining messages."""
        try:
            if self.message_queue:
                await self._send_batch()
            if self._session:
                if not self._session.closed:
                    await self._session.close()
                self._session = None
        except Exception as e:
            logging.error(f"Error during Discord logger cleanup: {e}", exc_info=True)

            
    def cleanup_discord_logger(logger_instance):
        asyncio.run(logger_instance.cleanup())


        
