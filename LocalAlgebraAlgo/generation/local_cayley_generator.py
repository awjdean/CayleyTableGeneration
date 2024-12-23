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
    Generates a Cayley table for action compositions using the local algorithm.

    This class extends NewActionsCayleyGenerator to handle local action compositions,
    where actions are only analyzed based on their effects from a specific initial
     state.

    The main difference is in how action compositions are computed - this class only
    considers the effects of actions from the initial state rather than all possible
     states.
    """

    def __init__(self) -> None:
        super().__init__()

    def _compute_composition_action_function(
        self, left_action: ActionType, right_action: ActionType
    ) -> ActionFunctionType:
        combined_action = left_action + right_action
        action_function = self.equiv_classes_generator._compute_action_function(
            combined_action
        )
        return action_function
