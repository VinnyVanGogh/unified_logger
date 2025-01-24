"""
This module serves as the entry point for the logging and result handling package of the application.

It imports and exposes key components such as Logger, LogLevel, and ResultLevel classes, along with various utilities and constants used for logging and result management. The module is designed to provide a centralized mechanism for logging and result reporting throughout the application.

"""

import logging
import traceback
import atexit
import sys
import os
import json

from ..input import Input
from .models import LogLevel, ResultLevel, Status
from .utils import (
    write_json_to_file,
    get_output_dir_path,
    calculate_directory_files_hash,
)
from .constants import (
    LOG_FILE_NAME,
    RESULT_FILE_NAME,
    PLUGIN_OUTPUT_DIR,
    WRITE_MODE,
    STATUS_KEY,
    MESSAGES_KEY,
    DATA_KEY,
    LEVEL_KEY,
    MESSAGE_KEY,
    DEFAULT_KEY,
    DEFAULT_LANG,
    SHA256,
)


__all__ = [
    "Logger",
    "LogLevel",
    "ResultLevel",
]


DEFAULT_LOG_FORMAT = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

class Logger:
    """
    Logger is a singleton class that serves as a wrapper around the built-in logging module. It provides functionality for logging messages of various levels such as info, error, debug, critical, exception, and fatal into a log file. This log file can then be attached to a ticket for debugging or audit purposes.

    In addition to logging messages, the Logger class also provides functionality to add messages with different levels into a result.json file. These messages can be displayed in a UI to provide feedback or status updates to the user.

    The Logger class also provides a method to log data into the result.json file. This can be useful for storing the results of a process or operation.

    Attributes:
    - _instance: The singleton instance of the class.
    - _logger: The logger instance.
    - _result_messages: A list to store the result messages.
    - _data: A dictionary to store the data.
    - _status: A string to store the status of the logger.
    """

    _instance = None
    _logger: logging.Logger = None
    _result_messages: list = []
    _data: dict = {}
    _status: str = ""
    _output_dir: str = ""
    
    def __new__(cls, *args, **kwargs):
        """
        Overrides the __new__ method to ensure only one instance of Logger is created.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, level: LogLevel = LogLevel.INFO):
        """
        Initializes the Logger instance. If the logger is not already initialized,
        it initializes it by creating a new logger instance with the given level.
        """
        if self._logger is None:
            try:
                input_data = Input()
                self._output_dir = get_output_dir_path(input_data.get_value(PLUGIN_OUTPUT_DIR))
            except Exception:
                self._output_dir = get_output_dir_path()
                
            self.init_logger(level)
            atexit.register(self.close)

    def init_logger(self, level):
        """
        Initializes the logger with the given level and adds a file handler to it.
        """
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level)
        self._logger.handlers.clear()

        logfile = os.path.join(self._output_dir, LOG_FILE_NAME)
        file_handler = logging.FileHandler(filename=logfile, mode=WRITE_MODE)
        file_handler.setLevel(level)
        file_handler.setFormatter(DEFAULT_LOG_FORMAT)
        self._logger.addHandler(file_handler)

    def close(self):
        """
        Closes the logger by creating the result file.
        """
        self._create_result_file()
       
        hashes = calculate_directory_files_hash(self._output_dir, SHA256)        
        sys.stdout.write(f"{json.dumps(hashes)}\n")

    def _create_result_file(self):
        """
        Creates the result file if there are result messages or data.
        """
        if not self._result_messages and not self._data:
            return

        log_data = {
            STATUS_KEY: self._status,
            MESSAGES_KEY: self._result_messages,
            DATA_KEY: self._data,
        }
        result_file_path = os.path.join(self._output_dir, RESULT_FILE_NAME)

        try:
            write_json_to_file(result_file_path, log_data)
        except Exception as e:
            self.exception(e, f"Failed to write result into {result_file_path} file")
            raise e

    def _append_result(self, level: ResultLevel, msg: str):
        """
        Appends a result message to the list of result messages and updates the status.
        """
        message = {
            LEVEL_KEY: level,
            MESSAGE_KEY: {
                DEFAULT_KEY: {DEFAULT_LANG: msg},
            },
        }

        self._result_messages.append(message)

        if self._status != Status.FAILED:
            self._status = (Status.SUCCESS if level != ResultLevel.ERROR else Status.FAILED)

    def debug(self, msg):
        """
        Logs a debug message.
        """
        self._logger.debug(msg)

    def info(self, msg):
        """
        Logs an info message.
        """
        self._logger.info(msg)

    def warning(self, msg):
        """
        Logs a warning message.
        """
        self._logger.warning(msg)

    def error(self, msg):
        """
        Logs an error message.
        """
        self._logger.error(msg)

    def critical(self, msg):
        """
        Logs a critical message.
        """
        self._logger.critical(msg)

    def fatal(self, msg):
        """
        Logs a fatal message and exits the program.
        """
        self.critical(msg)
        exit(1)

    def exception(self, e, msg=None, stack_info=False):
        """
        Logs an exception with an optional message and stack trace.
        """
        if msg is None:
            msg = "An exception occurred."
        exception_message = str(e)
        if stack_info:
            exception_traceback = traceback.format_exc()
            exception_message = f"{exception_message}\n{exception_traceback}"

        self._logger.critical(exception_message)
        self._logger.error(f"{msg}, See previous log messages for more details.")

    def result_data(self, data: dict):
        """
        Sets the data for the result.
        """
        self._data = data

    def result_message(self, level: ResultLevel, msg: str):
        """
        Appends a result message with the given level and message.
        """
        self._append_result(level, msg)

    def result_success_message(self, msg: str):
        """
        Appends a success result message.
        """
        self.result_message(ResultLevel.SUCCESS, msg)

    def result_failed_message(self, msg: str):
        """
        Appends a failed result message.
        """
        self.result_message(ResultLevel.FAILED, msg)
