#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ./src/loggers/types.py

from enum import Enum, auto
from typing import Set

class LoggerType(Enum):
    """Supported logger types for the unified logging system."""
    LOCAL = auto()
    ASIO = auto()
    DISCORD = auto()
    
    @classmethod
    def all_types(cls) -> Set['LoggerType']:
        """Return set of all available logger types."""
        return {cls.LOCAL, cls.ASIO, cls.DISCORD}
        
    def __str__(self) -> str:
        """String representation for configuration display."""
        return self.name.lower()