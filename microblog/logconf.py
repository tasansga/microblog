#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Logging set up and configuration
"""

from enum import Enum
import logging.config
import os


class LogConfig(Enum):
    """
    Enum to separate log environments, specifically WSGI and console/STDOUT
    """

    WSGI = 1
    CLI = 2


def set_logging(log_config):
    """
    Set logging configuration that should be used
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_config = _get_logging_config(log_config, log_level)
    logging.config.dictConfig(log_config)
    if logging.DEBUG >= logging.root.level:
        # Conveniently enable sqlalchemy logging if log level is DEBUG
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def _get_logging_config(log_config, log_level):
    """
    Get logging configuration for use with logging.config.dictConfig
    """
    if not isinstance(log_config, LogConfig):
        raise ValueError(
            f"log_config parameter must be of type LogConfig but is {type(log_config)}"
        )
    # Default represents LogConfig.CLI
    stream = "ext://sys.stdout"
    handler = "console"
    log_format = "%(message)s"
    if log_config == LogConfig.CLI:
        pass
    elif log_config == LogConfig.WSGI:
        stream = "ext://flask.logging.wsgi_errors_stream"
        handler = "wsgi"
        log_format = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    else:
        logging.error(
            """Unhandled LogConfig enum value, defaulting to CLI.
            This is probably a bug in logconf. log_config is: %s""",
            log_config,
        )
    return {
        "version": 1,
        "formatters": {
            "default": {
                "format": log_format,
            }
        },
        "handlers": {
            handler: {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": stream,
            }
        },
        "root": {"level": log_level, "handlers": ["console"]},
    }
