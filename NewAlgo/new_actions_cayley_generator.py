"""
Module for generating Cayley tables of action compositions.
"""

import time

from cayley_tables.tables.cayley_table_actions import CayleyTableActions
from cayley_tables.utils.equiv_classes import EquivClasses
from NewAlgo.actions_to_action_functions_map import (
    ActionFunctionType,
)
from NewAlgo.new_equiv_classes_generator import NewEquivClassGenerator
from utils.type_definitions import ActionType


def _compose_action_functions(
    left_action_function: ActionFunctionType,
    right_action_function: ActionFunctionType,
) -> ActionFunctionType:
    """
    Compose two action functions into a single function.

    Args:
        left_action_function: Function applied second
        right_action_function: Function applied first

    Returns:
        The composed function mapping states to their final states
    """
    composed_action_function: ActionFunctionType = {}
    for r_initial_state in right_action_function.keys():
        r_final_state = right_action_function[r_initial_state]
        # In left_action_function, find the final state with the initial state of
        #  r_final_state.
        for l_initial_state in left_action_function.keys():
            if l_initial_state == r_final_state:
                l_final_state = left_action_function[l_initial_state]
                composed_action_function[r_initial_state] = l_final_state
                break

    return composed_action_function


class NewActionsCayleyGenerator:
    """
    Generates a Cayley table for action compositions using the new algorithm.

    This class builds a complete action composition table by:
    1. Taking distinct actions and equivalence classes as input
    2. Computing compositions between actions using their action functions
    3. Finding which equivalence class contains each composed action

    The resulting table maps pairs of actions to their composition outcome.
    """

    PROGRESS_UPDATE_INTERVAL = 10.0  # seconds

    def __init__(self) -> None:
        """Initialize the generator."""
        self.cayley_table_actions: CayleyTableActions
        self.equiv_classes_generator: NewEquivClassGenerator
        # Add tracking dictionary
        self.progress_tracking = {
            "total_elements": 0,
            "completed_elements": 0,
            "last_update_time": 0.0,
            "start_time": 0.0,
        }

    def generate(self, equiv_classes_generator: NewEquivClassGenerator) -> None:
        """
        Generate the complete Cayley table for action compositions.

        Args:
            equiv_classes_generator: Generator containing distinct actions and their
                equivalence classes
        """
        print("\nGenerating actions Cayley table...")
        self.progress_tracking["start_time"] = time.time()
        self.progress_tracking["last_update_time"] = self.progress_tracking[
            "start_time"
        ]

        self.equiv_classes_generator = equiv_classes_generator
        self.cayley_table_actions = CayleyTableActions()

        equiv_classes: EquivClasses = equiv_classes_generator.get_equiv_classes()
        equiv_classes_labels = equiv_classes.get_labels()

        # Calculate total elements
        self.progress_tracking["total_elements"] = len(equiv_classes_labels) ** 2

        self._generate_composition_table(equiv_classes_labels)

        time_taken = time.time() - self.progress_tracking["start_time"]
        print(f"\nActions Cayley table generated (Total taken: {time_taken:.2f}s)")

    def get_actions_cayley_table(self) -> CayleyTableActions:
        """Return the generated Cayley table for actions."""
        return self.cayley_table_actions

    def _generate_composition_table(
        self,
        equiv_classes_labels: list[ActionType],
    ) -> None:
        """
        Generate the composition table entries.

        For each pair of actions (a,b), computes their composition by:
        1. Getting their action functions
        2. Composing the functions
        3. Finding which action has the composed function

        Args:
            equiv_classes_labels: Labels of equivalence classes to use as table indices
        """
        current_time = time.time()

        for right_action in equiv_classes_labels:
            self.cayley_table_actions.data[right_action] = {}
            for left_action in equiv_classes_labels:
                composed_action = self._compute_composition(left_action, right_action)
                self.cayley_table_actions.data[right_action][left_action] = (
                    composed_action
                )

                # Update progress
                self.progress_tracking["completed_elements"] += 1
                current_time = time.time()
                if (
                    current_time - self.progress_tracking["last_update_time"]
                    >= self.PROGRESS_UPDATE_INTERVAL
                ):
                    self._display_progress()
                    self.progress_tracking["last_update_time"] = current_time

    def _compute_composition(
        self,
        left_action: ActionType,
        right_action: ActionType,
    ) -> ActionType:
        """
        Compute a single composition of two actions.

        Args:
            left_action: The action applied second
            right_action: The action applied first

        Returns:
            The action that represents the composition result
        """

        composed_action_function = self._compute_composition_action_function(
            left_action, right_action
        )

        action_functions_maps = self.equiv_classes_generator.get_action_functions_maps()
        # Find action in distinct_actions that has the composed_action_function
        composed_action = action_functions_maps.get_action_from_action_function(
            composed_action_function
        )
        return composed_action

    def _compute_composition_action_function(
        self, left_action: ActionType, right_action: ActionType
    ) -> ActionFunctionType:
        action_functions_maps = self.equiv_classes_generator.get_action_functions_maps()
        # Get action_function for right_action and left_action
        right_action_function = action_functions_maps.get_action_function_from_action(
            right_action
        )
        left_action_function = action_functions_maps.get_action_function_from_action(
            left_action
        )
        # Compose the action functions
        composed_action_function = _compose_action_functions(
            left_action_function, right_action_function
        )

        return composed_action_function

    def _display_progress(self) -> None:
        """Display the current progress of table generation."""
        completed = self.progress_tracking["completed_elements"]
        total = self.progress_tracking["total_elements"]
        elapsed_time = time.time() - self.progress_tracking["start_time"]

        # Calculate percentage and rate
        percentage = (completed / total) * 100
        rate = completed / elapsed_time if elapsed_time > 0 else 0

        # Estimate time remaining
        remaining_elements = total - completed
        time_remaining = remaining_elements / rate if rate > 0 else 0

        print(
            f"\r\tProgress: {percentage:.1f}% ({completed}/{total} elements) "
            f"| Rate: {rate:.1f} elements/sec "
            f"| Est. remaining: {time_remaining:.1f}s",
            end="",
            flush=True,
        )
