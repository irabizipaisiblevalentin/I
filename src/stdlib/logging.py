"""logging — Logging framework for the I language.

Provides structured logging with levels, formatters, and handlers.
"""

from __future__ import annotations

import logging as _logging
import sys
from typing import Any, Optional


# Log levels
DEBUG = _logging.DEBUG
INFO = _logging.INFO
WARNING = _logging.WARNING
ERROR = _logging.ERROR
CRITICAL = _logging.CRITICAL


class Logger:
    """Named logger with configurable level and output."""

    def __init__(self, name: str = "i", level: int = INFO,
                 fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s") -> None:
        self._logger = _logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.handlers.clear()
        handler = _logging.StreamHandler(sys.stderr)
        handler.setFormatter(_logging.Formatter(fmt))
        self._logger.addHandler(handler)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.critical(msg, *args, **kwargs)

    def set_level(self, level: int) -> None:
        self._logger.setLevel(level)

    def add_file(self, path: str, encoding: str = "utf-8") -> None:
        handler = _logging.FileHandler(path, encoding=encoding)
        handler.setFormatter(_logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        self._logger.addHandler(handler)


_default_logger = Logger("i")


def debug(msg: str, *args: Any, **kwargs: Any) -> None:
    _default_logger.debug(msg, *args, **kwargs)


def info(msg: str, *args: Any, **kwargs: Any) -> None:
    _default_logger.info(msg, *args, **kwargs)


def warning(msg: str, *args: Any, **kwargs: Any) -> None:
    _default_logger.warning(msg, *args, **kwargs)


def error(msg: str, *args: Any, **kwargs: Any) -> None:
    _default_logger.error(msg, *args, **kwargs)


def critical(msg: str, *args: Any, **kwargs: Any) -> None:
    _default_logger.critical(msg, *args, **kwargs)


def get_logger(name: str) -> Logger:
    return Logger(name)
