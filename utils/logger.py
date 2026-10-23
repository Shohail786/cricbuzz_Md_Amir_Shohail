"""Logging helper: one consistently formatted logger per module."""
from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger (configured once, safe to call repeatedly)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
