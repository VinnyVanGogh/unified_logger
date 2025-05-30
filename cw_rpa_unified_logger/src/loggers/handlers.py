#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/utils/handlers.py

import logging
import colorlog
from pathlib import Path
from datetime import datetime, UTC

class LogHandlerFactory:
    """
    Factory class for creating and configuring logging handlers.
    Supports console and file handlers with customizable formatting.
    """
    
    @staticmethod
    def create_console_handler(
        level: int,
        format_string: str | None = None,
        log_colors: dict[str, str] | None = None
    ) -> logging.Handler:
        """
        Create a console handler with color support.
        """
        handler = colorlog.StreamHandler()
        handler.setLevel(level)  # <- Ensure handler respects the configured level

        if format_string is None:
            format_string = (
                '%(asctime)s - [%(process)d] - %(log_color)s%(levelname)s%(reset)s - '
                '%(log_color)s%(message)s%(reset)s'
            )
            
        if log_colors is None:
            log_colors = {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
            
        formatter = colorlog.ColoredFormatter(
            format_string,
            log_colors=log_colors,
            reset=True,
            style='%'
        )
        handler.setFormatter(formatter)
        return handler

        
    @staticmethod
    def create_file_handler(
        level: int,
        log_file: Path,
        format_string: str | None = None,
        mode: str = 'a',
        encoding: str = 'utf-8'
    ) -> logging.Handler:
        """
        Create a file handler for writing log messages to a file.
        """
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(
            log_file,
            mode=mode,
            encoding=encoding
        )
        handler.setLevel(level)
        
        if format_string is None:
            format_string = '%(asctime)s - [%(process)d] - %(levelname)s - %(message)s'
            
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        
        # Write initialization marker if in write mode
        if mode == 'w':
            with open(log_file, 'w', encoding=encoding) as f:
                f.write(f"Log initialized at {datetime.now(UTC)}\n")
                
        return handler
        
    @classmethod
    def create_handlers(
        cls,
        level: int,
        log_file: Path | None = None,
        enable_console: bool = True,
        terminal_level: int = logging.WARNING  # Add terminal level parameter
    ) -> list[logging.Handler]:
        """
        Create multiple handlers at once.
        """
        handlers = []
        
        if enable_console:
            handlers.append(cls.create_console_handler(terminal_level))  # Use terminal_level for console
        
        if log_file is not None:
            handlers.append(cls.create_file_handler(level, log_file))
        
        return handlers
