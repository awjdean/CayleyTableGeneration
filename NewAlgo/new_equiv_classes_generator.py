"""
Module for generating equivalence classes of actions based on their effects on
 states.

This module provides functionality to find distinct actions in a world by analysing
 their effects on states. Actions that produce the same state transformations are
 grouped into equivalence classes.
"""

import copy
import itertools
import time

from cayley_tables.utils.action_outcome import generate_action_outcome
from cayley_tables.utils.equiv_classes import EquivClasses
from utils.type_definitions import ActionType, MinActionsType, StateType
from worlds.base_world import BaseWorld

ActionFunctionType = dict[StateType, StateType]
DistinctActionsDataType = dict[ActionType, ActionFunctionType]


class ActionsActionFunctionsMap:
    def __init__(self) -> None:
        self.data: DistinctActionsDataType = {}

    def add_action(
        self, action: ActionType, action_function: ActionFunctionType
    ) -> None:
        """Add an action to the distinct actions dictionary."""
        self.data[action] = action_function

    def get_actions_from_length(self, length: int) -> list[ActionType]:
        result: list[ActionType] = []
        for action in self.data:
            if len(action) == length:
                result.append(action)
        return result

    def action_function_exists(self, action_function: ActionFunctionType) -> bool:
        """Check if an action function already exists in distinct_actions."""
        return any(
            existing_function == action_function
            for existing_function in self.data.values()
        )

    def get_action_from_action_function(
        self, action_function: ActionFunctionType
    ) -> ActionType:
        """Find the representative action for a given action function."""
        for action, existing_function in self.data.items():
            if existing_function == action_function:
                return action
        raise ValueError("Action function not found in self.distinct_actions")

    def get_num_actions(self) -> int:
        """Return the number of distinct actions."""
        return len(self.data)

    def get_action_function_from_action(self, action: ActionType) -> ActionFunctionType:
        """Return the action function for a given action."""
        return self.data[action]


class NewEquivClassGenerator:
    """
    Generates equivalence classes of actions based on their effects on states.

    This class analyzes actions by their effects on states, grouping together actions
    that produce identical state transformations. It builds these groups incrementally,
    starting with minimal actions and composing them to find all distinct actions.

    Attributes:
        min_actions: List of minimal actions from the world
        distinct_actions: Dictionary mapping actions to their state transformation
         functions
        equiv_classes: EquivClasses object storing the equivalence classes
    """

    def __init__(self, world: BaseWorld):
        """Initialize the generator with a world.

        Args:
            world: The world to analyze actions in
        """
        self.min_actions: MinActionsType = world.get_min_actions()
        self._world: BaseWorld = world

        self.distinct_actions: ActionsActionFunctionsMap = ActionsActionFunctionsMap()
        self.equiv_classes: EquivClasses = EquivClasses()
        self._last_print_time: float = 0

    def generate(self) -> None:
        """
        Generate all equivalence classes of actions.

        This method:
        1. Finds distinct minimal actions
        2. Iteratively composes actions to find new distinct ones
        3. Groups equivalent actions together
        4. Continues until no new distinct actions are found
        """
        print("\nGenerating equivalence classes.")
        start_time = time.time()
        self._find_distinct_min_actions()
        distinct_min_actions: DistinctActionsDataType = copy.deepcopy(
            self.distinct_actions.data
        )

        num_new_actions = self.distinct_actions.get_num_actions() - 0
        time_taken = time.time() - start_time
        print(
            f"\tAction length: 1,"
            f"\tDistinct actions: {self.distinct_actions.get_num_actions()}"
            f" (+{num_new_actions}),"
            f"\tTime: {time_taken:.2f}s"
        )

        for current_length in itertools.count(2):
            iteration_start = time.time()
            prev_distinct_count = self.distinct_actions.get_num_actions()

            # Generate all actions of length current_length by composing
            #  distinct_min_actions to each element of length current_length - 1.
            prev_actions = self.distinct_actions.get_actions_from_length(
                length=current_length - 1
            )
            new_action_sequences = self._generate_new_action_sequences(
                prev_actions, distinct_min_actions
            )
            # Check if any of the new actions are distinct.
            for action in new_action_sequences:
                self._process_action(action)

            num_new_actions = (
                self.distinct_actions.get_num_actions() - prev_distinct_count
            )
            time_taken = time.time() - iteration_start
            print(
                f"\tAction length: {current_length},"
                f"\tDistinct actions: {self.distinct_actions.get_num_actions()} "
                f"(+{num_new_actions}), "
                f"\tTime: {time_taken:.2f}s"
            )

            # If no new distinct actions were found, halt.
            if prev_distinct_count == self.distinct_actions.get_num_actions():
                total_time = time.time() - start_time
                print(
                    f"\nEquiv classes generated:"
                    f"\n\tAction length: {current_length},"
                    f"\tDistinct actions: {prev_distinct_count},"
                    f"\t\tTotal time: {total_time:.2f}s"
                )
                break

    def get_equiv_classes(self) -> EquivClasses:
        """Return the equivalence classes generated by this object.

        Returns:
            The EquivClasses object containing the equivalence classes
        """
        return self.equiv_classes

    def get_distinct_actions(self) -> ActionsActionFunctionsMap:
        """Return the distinct actions generated by this object.

        Returns:
            The DistinctActions object containing the distinct actions
        """
        return self.distinct_actions

    def _find_distinct_min_actions(self) -> None:
        """Find all distinct minimal actions by processing each minimal action."""
        for min_action in self.min_actions:
            self._process_action(min_action)

    def _process_action(self, action: ActionType) -> None:
        """
        Process an action and add it to the appropriate equivalence class.

        Args:
            action: The action to process
        """
        action_function: ActionFunctionType = self._compute_action_function(action)
        if self.distinct_actions.action_function_exists(action_function):
            self.equiv_classes.add_element(
                element=action,
                class_label=self.distinct_actions.get_action_from_action_function(
                    action_function
                ),
            )
        else:
            self.distinct_actions.add_action(action, action_function)
            self.equiv_classes.create_new_class(
                class_label=action, elements=[action], outcome=(None,)
            )

    def _compute_action_function(self, action: ActionType) -> ActionFunctionType:
        """Compute the state transformation function for an action.

        Args:
            action: The action to compute the function for

        Returns:
            Dictionary mapping each state to the resulting state after applying the
              action
        """
        action_function: ActionFunctionType = {}
        for state in self._world.get_possible_states():
            action_function[state] = generate_action_outcome(action, state, self._world)
        return action_function

    def _generate_new_action_sequences(
        self,
        prev_actions: list[ActionType],
        distinct_min_actions: DistinctActionsDataType,
    ) -> list[ActionType]:
        """
        Generate new action sequences by composing previous actions with minimal
         actions.

        Args:
            prev_actions: List of actions from the previous iteration
            distinct_min_actions: Dictionary of minimal actions and their functions

        Returns:
            List of new action sequences
        """
        new_actions: list[ActionType] = []
        for prev_action in prev_actions:
            for min_action in distinct_min_actions:
                new_action = min_action + prev_action
                new_actions.append(new_action)
        return new_actions


def sort_elements(elements):
    # Sort by length first, then alphabetically
    sorted_elements = sorted(list(elements))
    sorted_elements = sorted(sorted_elements, key=len)
    return sorted_elements