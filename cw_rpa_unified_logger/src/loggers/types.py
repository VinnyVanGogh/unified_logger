#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/types.py

from enum import Enum
from typing import Union, Set, List
import logging

class LoggerType(Enum):
    """Supported logger types for the unified logging system."""
    LOCAL = "local"
    ASIO = "asio"
    DISCORD = "discord"
    
    @classmethod
    def all_types(cls) -> Set['LoggerType']:
        """Return set of all available logger types."""
        return {cls.LOCAL, cls.ASIO, cls.DISCORD}
    
    @classmethod
    def get_valid_types(cls) -> Set[str]:
        """Return set of valid logger type names."""
        return {t.value for t in cls}
    
    @classmethod 
    def from_input(cls, types: Union[str, Set[str], List[str], None]) -> Set['LoggerType']:
        """Convert input to LoggerType set with validation."""
        if types is None:
            return cls.all_types()
        
        if isinstance(types, str):
            # Split and convert string input
            return {
                cls[t.strip().upper()] 
                for t in types.split(',') 
                if t.strip().upper() in cls._member_names_
            }
        
        # Assume it's an iterable of strings
        return {
            cls[t.strip().upper()]
            for t in types
            if isinstance(t, str) and t.strip().upper() in cls._member_names_
        }
    
    @classmethod 
    def split_multiple(cls, types: str) -> Set['LoggerType']:
        """Split comma-separated string into set of LoggerType."""
        return {
            cls[t.strip().upper()] 
            for t in types.split(',') 
            if t.strip().upper() in cls._member_names_
        }

    def __str__(self) -> str:
        return self.value