#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/base.py

from abc import ABC, abstractmethod
from typing import Any

class BaseLogger(ABC):
    """
    Abstract base class defining the interface for all logger implementations.
    Ensures consistent logging behavior across different logging backends.
    """
    
    @abstractmethod
    def log(self, level: int, message: str) -> None:
        """
        Log a message at the specified level.
        
        Args:
            level (int): The logging level (DEBUG, INFO, etc.)
            message (str): The message to log
        """
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """Log a debug message."""

    @abstractmethod
    def info(self, message: str) -> None:
        """Log an info message."""

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log a warning message."""

    @abstractmethod
    def error(self, message: str) -> None:
        """Log an error message."""

    @abstractmethod
    def critical(self, message: str) -> None:
        """Log a critical message."""
        
    @abstractmethod
    def exception(self, e: Exception, message: str) -> None:
        """
        Log an exception with additional context.
        
        Args:
            e (Exception): The exception that occurred
            message (str): Additional context about the exception
        """
        
    @abstractmethod
    def result_data(self, data: dict[str, Any]) -> None:
        """
        Log structured result data.
        
        Args:
            data (dict): The data to log
        """

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources used by the logger."""
