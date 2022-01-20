"""
The logging module provides access to an initiated logging system.
"""

import logging

logging.basicConfig(
    format="%(process)d.%(thread)d %(name)s in %(funcName)s at %(filename)s:%(lineno)d %(levelname)s: %(message)s",
    level=logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger
    :param name: Logger name
    :return: Logger
    """
    return logging.getLogger(name)
