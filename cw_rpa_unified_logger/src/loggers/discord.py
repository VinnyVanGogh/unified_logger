#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./cw_rpa_unified_logger/src/loggers/discord.py

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
    
    DEFAULT_COLORS = {
        logging.DEBUG: 0x7F7F7F,
        logging.INFO: 0x3498DB,
        logging.WARNING: 0xF1C40F,
        logging.ERROR: 0xE74C3C,
        logging.CRITICAL: 0x992D22
    }
    
    def __init__(self, discord_webhook_url: str, logger_name: str = "Application Logger"):
        """
        Initialize Discord logger with webhook configuration.
        """
        self.discord_webhook_url = discord_webhook_url
        self.username = logger_name
        self._session = None
        self._lock = asyncio.Lock()
        self._running = True
        self.message_queue = []
        self.last_batch_time = time.time()
        self.batch_size = 5
        self.batch_interval = 5  
        self.max_retries = 3
        self.retry_delay = 1
        self.max_embed_length = 1900
        self._initialize_logging()
        self._batch_task = None
        self.loop = None  # Remove manual loop creation

    async def initialize(self) -> None:
        """Async initialization for Discord logger."""
        webhook_valid = await self._check_webhook()
        if webhook_valid:
            self._batch_task = asyncio.create_task(self._batch_processor())
        else:
            self._running = False
            self.logger.warning("Discord logging disabled due to invalid webhook")

    async def _batch_processor(self):
        """Background task to process message batches."""
        while self._running:
            try:
                current_time = time.time()
                if (len(self.message_queue) >= self.batch_size or 
                    (self.message_queue and current_time - self.last_batch_time >= self.batch_interval)):
                    async with self._lock:
                        await self._send_batch()
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(1)

    async def _ensure_session(self) -> bool:
        """Ensure aiohttp session is initialized."""
        try:
            if self._session is None or self._session.closed:
                self.logger.debug("Creating new aiohttp session")
                self._session = aiohttp.ClientSession()
                return True
            return True
        except Exception as e:
            self.logger.error(f"Session initialization failed with: {str(e)}")
            self._session = None
            return False

    async def _send_batch(self, retries: int = 0) -> bool:
        """Send accumulated messages as a batch with retry logic."""
        if not self.message_queue:
            return True

        self.logger.debug(f"Attempting to send batch (retry {retries})")
        
        try:
            if not await self._ensure_session():
                self.logger.error("Failed to ensure session")
                return False

            if self._session is None:
                self.logger.error("Session is None after ensure_session")
                return False

            self.logger.debug(f"Preparing payload with {len(self.message_queue[:10])} messages")
            payload = {
                "username": self.username,
                "embeds": self.message_queue[:10]
            }

            self.logger.debug("Sending request to Discord webhook")
            
            async with self._session.post(
                self.discord_webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                self.logger.debug(f"Got response status: {response.status}")
                
                if response.status == 429:
                    retry_after = (await response.json()).get('retry_after', self.retry_delay)
                    self.logger.warning(f"Rate limited. Retry after: {retry_after}s")
                    if retries < self.max_retries:
                        await asyncio.sleep(retry_after)
                        return await self._send_batch(retries + 1)
                    return False

                if response.status in [502, 503, 504]:
                    self.logger.warning(f"Gateway error {response.status}")
                    if retries < self.max_retries:
                        await asyncio.sleep(self.retry_delay * (retries + 1))
                        return await self._send_batch(retries + 1)

                # 204 is success for Discord webhook
                if response.status == 204:
                    self.logger.debug("Successfully sent batch")
                    self.message_queue = self.message_queue[10:]
                    self.last_batch_time = time.time()
                    return True

                # Only raise for non-204 responses
                if response.status != 204:
                    await response.raise_for_status()
                
                return True

        except Exception as e:
            self.logger.error(f"Error sending batch: {str(e)}\nType: {type(e)}")
            if retries < self.max_retries:
                self.logger.debug(f"Retrying after error (attempt {retries + 1})")
                await asyncio.sleep(self.retry_delay)
                if self._session and not self._session.closed:
                    await self._session.close()
                self._session = None
                return await self._send_batch(retries + 1)
            return False

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

    async def _check_webhook(self) -> bool:
        """
        Check if the webhook URL is valid by sending a test request.
        
        Returns:
            bool: True if webhook is valid and accessible, False otherwise
        """
        try:
            if not self.discord_webhook_url.startswith("https://discord.com/api/webhooks/"):
                self.logger.warning("Invalid webhook URL format")
                return False
                
            await self._ensure_session()
            if self._session is None:
                return False
                
            test_payload = {
                "username": self.username,
                "embeds": [{
                    "title": "Logger Initialization",
                    "description": "Testing webhook connectivity",
                    "color": self.DEFAULT_COLORS[logging.INFO]
                }]
            }
            
            async with self._session.post(
                self.discord_webhook_url,
                json=test_payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 204:
                    return True
                    
                if response.status == 404:
                    self.logger.warning("Webhook not found - Discord logging will be disabled")
                    return False
                    
                if response.status == 401:
                    self.logger.warning("Unauthorized webhook - Discord logging will be disabled")
                    return False
                    
                # Any other error
                self.logger.warning(f"Webhook validation failed with status {response.status}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Failed to validate webhook: {str(e)}")
            return False

    def _sync_log(self, level: int, message: str) -> None:
        """Synchronous wrapper for async logging."""
        if not self._running:
            return
            
        try:
            embed = self._create_embed(level, message)
            self.message_queue.append(embed)
        except Exception as e:
            self.logger.error(f"Logging failed for DiscordLogger: {str(e)}")

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
            self.logger.error(f"Failed to format result data for Discord: {e}")
            
    def _initialize_logging(self):
        """Initialize the logger with a specific format."""
        self.logger = logging.getLogger('DiscordLogger')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - [%(process)d] - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def cleanup(self) -> None:
        """Clean up Discord logger resources."""
        self._running = False
        try:
            if self.message_queue:
                success = await self._send_batch()
                if not success:
                    self.logger.warning("Failed to send final batch during cleanup")
                    
            if hasattr(self, '_batch_task') and self._batch_task and not self._batch_task.done():
                self._batch_task.cancel()
                try:
                    await self._batch_task
                except asyncio.CancelledError:
                    pass
                    
            if self._session:
                if not self._session.closed:
                    await self._session.close()
                self._session = None
                    
        except Exception as e:
            self.logger.error(f"Discord cleanup failed: {e}")

    def cleanup_discord_logger(self):
        """Helper to run cleanup synchronously."""
        if not hasattr(self, 'loop') or self.loop is None:
            return
            
        try:
            # Add is_closed check before accessing
            if self.loop.is_closed():
                return
                
            if not self.loop.is_running():
                self.loop.run_until_complete(self.cleanup())
            else:
                asyncio.run_coroutine_threadsafe(self.cleanup(), self.loop)
                
        except Exception as e:
            self.logger.error(f"Synchronous cleanup failed: {str(e)}")
        finally:
            try:
                if not self.loop.is_closed():
                    self.loop.close()
            except Exception:
                pass

    def __del__(self):
        """Ensure cleanup on deletion."""
        try:
            self.cleanup_discord_logger()
        except Exception as e:
            self.logger.error(f"Deletion cleanup failed: {str(e)}")