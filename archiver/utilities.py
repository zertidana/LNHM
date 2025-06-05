"""A script containing utility functions."""
from logging import getLogger, INFO, StreamHandler
from sys import stdout


def get_logger():
    """Return logger with desired config."""
    return getLogger(__name__)


def set_logger():
    """Set logger configuration."""
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    logger.addHandler(StreamHandler(stdout))
