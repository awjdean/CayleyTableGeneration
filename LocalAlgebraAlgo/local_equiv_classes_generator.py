"""
Module for generating equivalence classes of actions based on their effects on
 states.

This module provides functionality to find distinct actions in a world by analysing
 their effects on states. Actions that produce the same state transformations are
 grouped into equivalence classes.
"""

from cayley_tables.utils.action_outcome import generate_action_outcome
from NewAlgo.actions_to_action_functions_map import ActionFunctionType
from NewAlgo.new_equiv_classes_generator import NewEquivClassGenerator
from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


class LocalEquivClassGenerator(NewEquivClassGenerator):
    """
    Generates equivalence classes of actions based on their effects on a single initial
     state.

    This class analyzes actions by their effects on a specific initial state, grouping
     together
    actions that produce identical state transformations from that state. It builds
     these groups incrementally, starting with minimal actions and composing them to
     find all distinct actions.

    This is a local version of NewEquivClassGenerator that only considers
     transformations from a single initial state, rather than all possible states.

    Attributes:
        min_actions: List of minimal actions from the world
        distinct_actions: Dictionary mapping actions to their state transformation
         functions
        equiv_classes: EquivClasses object storing the equivalence classes
    """

    def __init__(self, world: BaseWorld):
        super().__init__(world)

    def generate(self, initial_state: StateType) -> None:
        """
        Generate all equivalence classes of actions based on their effects from the
         initial state.

        Args:
            initial_state: The state from which to analyze action effects
        """
        self._initial_state = initial_state
        super().generate()

    def get_world(self) -> BaseWorld:
        """
        Get the world object used by the generator.

        Returns:
            The world object
        """
        return self._world

    def get_initial_state(self) -> StateType:
        """
        Get the initial state used by the generator.

        Returns:
            The initial state
        """

        return self._initial_state

    def _compute_action_function(self, action: ActionType) -> ActionFunctionType:
        """
        Compute the action function for an action from the initial state only.

        Args:
            action: The action to compute the function for

        Returns:
            Dictionary mapping the initial state to the resulting state after applying
             the action
        """
        action_function: ActionFunctionType = {}
        action_function[self._initial_state] = generate_action_outcome(
            action, self._initial_state, self._world
        )
        return action_function
