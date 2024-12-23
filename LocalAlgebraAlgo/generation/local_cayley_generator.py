"""
Module for generating Cayley tables for local action compositions.
"""

from ActionFunctionsAlgo.generation.actions_to_action_functions_map import (
    ActionFunctionType,
)
from ActionFunctionsAlgo.generation.af_cayley_generator import AFCayleyGenerator
from utils.type_definitions import ActionType


class LocalActionsCayleyGenerator(AFCayleyGenerator):
    """
    Generates Cayley tables for action compositions based on an initial state.

    This class specializes the action composition algorithm to consider only the effects
    of actions from a specific initial state, rather than all possible states. This
    "local" approach leads to potentially different equivalence classes than the global
    approach.

    Key differences from AFCayleyGenerator:
    - Only considers action effects from the initial state
    - Actions are considered equivalent if they produce the same outcome from the
      initial state
    - Composition is computed based on local behavior only

    Inheritance:
        AFCayleyGenerator: Base class providing the general Cayley table generation
         framework
    """

    def __init__(self) -> None:
        """
        Initialize the LocalActionsCayleyGenerator.

        Calls the parent class (AFCayleyGenerator) initialization.
        """
        super().__init__()

    def _compute_composition_action_function(
        self, left_action: ActionType, right_action: ActionType
    ) -> ActionFunctionType:
        """
        Compute the action function resulting from composing two actions locally.

        This method overrides the parent class method to implement local composition,
        where actions are combined and evaluated based on their effects from the
        initial state only.

        Args:
            left_action: The action applied second in the composition
            right_action: The action applied first in the composition

        Returns:
            ActionFunctionType: The action function representing the local composition
        """
        combined_action = left_action + right_action
        action_function = self.equiv_classes_generator._compute_action_function(
            combined_action
        )
        return action_function
