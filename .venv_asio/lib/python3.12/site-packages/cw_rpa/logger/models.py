import logging


class LogLevel:
    """
    LogLevel is a simple class that provides constants for different logging levels.
    These constants are equivalent to the levels provided by the built-in logging module.
    """

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class ResultLevel:
    """
    ResultLevel is a class that provides constants for different result levels.
    These levels can be used to categorize the results of an operation or process.
    """

    SUCCESS = "success"
    FAILED = "error"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class Status:
    """
    Status is a class that provides constants for different statuses.
    These statuses can be used to indicate the success or failure of an operation or process.
    """

    SUCCESS = "Success"
    FAILED = "Failed"

