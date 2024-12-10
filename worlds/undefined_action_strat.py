from enum import Enum

from utils.type_definitions import StateType
from worlds.undefined_state import UndefinedStates


class UndefinedActionStrat(Enum):
    """
    Enum class defining strategies for handling undefined actions.

    Attributes:
        IDENTITY: Returns the original state unchanged
        MASKED: Returns a masked state (None,)
    """

    IDENTITY = "identity"
    MASKED = "masked"

    def _validate_instance(self) -> None:
        """Validates that the instance is either IDENTITY or MASKED."""
        if self not in (self.IDENTITY, self.MASKED):
            raise ValueError(f"Invalid undefined action strategy: {self}")

    def apply(self, state: StateType) -> StateType:
        """Apply the undefined action strategy to the given state.

        Args:
            state: The current state
            min_action: The minimum action (unused in current implementation)

        Returns:
            StateType: The transformed state based on the strategy
        """
        self._validate_instance()

        if self == self.IDENTITY:
            return state
        elif self == self.MASKED:
            return UndefinedStates.BASIC.value
        else:
            raise ValueError(f"Invalid undefined action strategy: {self}")
