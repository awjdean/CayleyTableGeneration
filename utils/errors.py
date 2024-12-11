"""Custom exceptions for the project."""


class CayleyTableError(ValueError):
    """Base exception for Cayley table related errors."""

    pass


class CompositionError(CayleyTableError):
    """Raised when action composition fails."""

    pass


class ValidationError(CayleyTableError):
    """Raised when Cayley table validation fails."""

    pass
