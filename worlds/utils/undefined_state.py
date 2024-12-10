"""
Module for defining undefined or null states used throughout the application.
This module provides enumeration of various undefined states that can be used
to represent missing, null, or uninitialized values in a type-safe way.
"""

from enum import Enum


class UndefinedStates(Enum):
    """
    Enumeration of undefined states used to represent null or uninitialized values.

    This enum provides type-safe alternatives to using None or null values directly,
    allowing for more explicit handling of undefined states in the application.
    """

    BASIC = (None,)
    """Basic undefined state representing a null or uninitialized value."""
