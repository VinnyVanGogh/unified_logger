#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/utils/message_formatter.py

import json
import re
from typing import Any

class MessageFormatter:
    """
    Handles message preprocessing including filtering, truncation,
    and structured data formatting.
    """
    
    def __init__(self, max_length: int, filter_patterns: list[str] | None = None):
        """
        Initialize the formatter with configuration.
        
        Args:
            max_length (int): Maximum allowed message length
            filter_patterns (list[str], optional): Regex patterns for filtering
        """
        self.max_length = max_length
        self._compiled_patterns = None
        if filter_patterns:
            self._compile_patterns(filter_patterns)
            
    def _compile_patterns(self, patterns: list[str]) -> None:
        """
        Precompile regex patterns for efficient filtering.
        
        Args:
            patterns (list[str]): List of regex pattern strings
        
        Raises:
            ValueError: If any pattern is invalid
        """
        self._compiled_patterns = []
        for pattern in patterns:
            try:
                self._compiled_patterns.append(re.compile(pattern))
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
                
    def filter_message(self, message: str) -> bool:
        """
        Check if message should be logged based on filter patterns.
        
        Args:
            message (str): Message to check
            
        Returns:
            bool: True if message should be logged, False if filtered out
        """
        if not isinstance(message, str) or not message.strip():
            return False
            
        if self._compiled_patterns:
            for pattern in self._compiled_patterns:
                if pattern.match(message):
                    return False
        return True
        
    def truncate_message(self, message: str) -> str:
        """
        Truncate message to maximum length if needed.
        
        Args:
            message (str): Message to truncate
            
        Returns:
            str: Truncated message
        """
        if len(message) > self.max_length:
            return f"{message[:self.max_length-3]}..."
        return message
        
    def format_data(self, data: Any) -> str:
        """
        Format complex data structures for logging.
        
        Args:
            data: Data structure to format
            
        Returns:
            str: Formatted string representation
        """
        try:
            return json.dumps(data, indent=2, default=str)
        except (TypeError, ValueError):
            return str(data)
            
    def process_message(self, message: str) -> str | None:
        """
        Apply all message processing steps.
        
        Args:
            message (str): Raw message
            
        Returns:
            str | None: Processed message or None if filtered
        """
        if not self.filter_message(message):
            return None
        return self.truncate_message(message)