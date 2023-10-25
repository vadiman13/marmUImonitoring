"""Module to setup logging"""

import logging
from typing import Optional

LOGGER_APP: Optional[logging.LoggerAdapter] = None

COUNTER_FULL = 0
COUNTER_ERROR = 0
COUNTER_SUCCESS = 0


class _CustomLogger(logging.LoggerAdapter):
    """Addition keywords for logging"""

    def process(self, msg, kwargs):
        extra = kwargs.get("extra")
        if not extra:
            kwargs["extra"] = extra = {}

        extra["mark"] = kwargs.pop("mark")
        extra["counter"] = kwargs.pop("counter")

        return msg, kwargs
    def debug(self, msg, *args, mark: bool = False, counter: bool = True, **kwargs):
        """
        Delegate a debug call to the underlying logger.
        """
        super().debug(msg, *args, mark=mark, counter=counter, **kwargs)

    def info(self, msg, *args, mark: bool = False, counter: bool = True, **kwargs):
        """
        Delegate an info call to the underlying logger.
        """
        super().info(msg, *args, mark=mark, counter=counter, **kwargs)

    def warning(self, msg, *args, mark: bool = False, counter: bool = True, **kwargs):
        """
        Delegate a warning call to the underlying logger.
        """
        super().warning(msg, *args, mark=mark, counter=counter, **kwargs)

    def error(self, msg, *args, mark: bool = False, counter: bool = True, **kwargs):
        """
        Delegate an error call to the underlying logger.
        """
        super().error(msg, *args, mark=mark, counter=counter, **kwargs)

    def exception(self, msg, *args, mark: bool = False, counter: bool = True, exc_info=True, **kwargs):
        """
        Delegate an exception call to the underlying logger.
        """
        super().exception(msg, *args, mark=mark, counter=counter, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, mark: bool = False, counter: bool = True, **kwargs):
        """
        Delegate a critical call to the underlying logger.
        """
        super().critical(msg, *args, mark=mark, counter=counter, **kwargs)


class _ResultFileFilter(logging.Filter):
    """A filter for file handler, which for result info by test"""

    def filter(self, record):
        # Add marker prefix to not empty message by level
        marker = ""

        global COUNTER_FULL, COUNTER_ERROR, COUNTER_SUCCESS

        if record.mark:

            if record.counter:
                COUNTER_FULL += 1

            if record.levelno == logging.INFO:
                marker = "🔵 "
                if record.counter:
                    COUNTER_SUCCESS += 1
            elif record.levelno == logging.ERROR:
                marker = "🔴 "
                if record.counter:
                    COUNTER_ERROR += 1

        record.marker = f"{marker}"

        return True


def _get_result_file_handler(file_name, level):
    """Form file handler to store result records for future send.
    Args:
        file_name (str): file name to store result
        level (int): logging level result logger file

    Returns:
        logging.FileHandler: result file handler
    """

    # Define result file handler
    handler_file_result = logging.FileHandler(
        filename=file_name,
        mode="w",
        encoding="utf-8"
    )

    # set level
    handler_file_result.setLevel(level)

    # add record filter
    handler_file_result.addFilter(_ResultFileFilter())

    # set format
    handler_file_result.setFormatter(logging.Formatter("%(marker)s%(message)s"))

    return handler_file_result


def get_logger(file_name_result, level_common=logging.INFO, level_result=logging.INFO):
    """Prepare logger to message handling.
    Args:
        file_name_result (str): file name which store result,
        level_common (int): logging level for common case,
        level_result (int): logging level result logger file

    Returns:
        _CustomLogger: custom logger adapter
    """

    global LOGGER_APP

    if LOGGER_APP:
        return LOGGER_APP

    # Root logger settings
    stream_handler = logging.StreamHandler()

    logging.basicConfig(
        level=level_common,
        format='%(asctime)s.%(msecs)03dZ - %(levelname)s: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        handlers=[stream_handler]
    )

    # App logger
    logger = logging.getLogger("APP")
    logger.addHandler(_get_result_file_handler(file_name_result, level_result))

    LOGGER_APP = _CustomLogger(logger, {})

    return LOGGER_APP
