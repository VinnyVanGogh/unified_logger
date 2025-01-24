"""
This package provides the core functionality for handling HTTP requests, logging, and input processing within the application.

It encapsulates the logic for sending HTTP requests, processing inputs, and logging messages in a structured manner. The package is designed to be used across various parts of the application to ensure consistency and reusability of the core components.

Modules:
    input: Handles the processing of input data.
    logger: Provides logging capabilities with different levels of severity.
    httpclient: Contains the functionality for making HTTP requests, including handling of headers, tokens, and different HTTP methods.

Classes:
    Input: A class for managing input data.
    Logger: A class for logging messages with support for different log levels.
    LogLevel: An enumeration of supported log levels.
    ResultLevel: An enumeration of result levels, used in logging outcomes.
    HttpClient: A class for making HTTP requests.
    HttpMethod: An enumeration of HTTP methods.
    Token: A class for managing authentication tokens.
    Headers: A class for managing HTTP request headers.
    HeaderKeys: An enumeration of common HTTP header keys.
    ContentTypes: An enumeration of MIME types for content negotiation.
    Integrations: An enumeration of supported external service integrations.

Usage:
    This package is intended to be used internally by the application to abstract away the complexities of HTTP communication, input processing, and logging. It provides a unified interface for these functionalities, making the application code cleaner and more maintainable.
"""


from .input import Input
from .logger import (
    Logger,
    LogLevel,
    ResultLevel,
)
from .httpclient import (
    HttpClient,
    HttpMethod,
    Token,   
    HeaderKeys,
    ContentTypes,
)


__all__ = [
    "Input",
    "Logger",
    "LogLevel",
    "ResultLevel",
    "HttpClient",
    "HttpMethod",
    "Token",    
    "HeaderKeys",
    "ContentTypes",
    "Integrations",
]
