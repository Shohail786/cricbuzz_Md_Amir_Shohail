"""Project-specific exceptions so pages can catch precise error types."""
from __future__ import annotations


class CricbuzzError(Exception):
    """Base class for all application errors."""


class ApiError(CricbuzzError):
    """Raised when the Cricbuzz API call fails or returns unusable data."""


class DatabaseError(CricbuzzError):
    """Raised when a database operation fails."""


class ValidationError(CricbuzzError):
    """Raised when user input fails validation. Holds a list of messages."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors
