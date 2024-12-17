import time

from cayley_tables.tables.cayley_table_actions import CayleyTableActions
from cayley_tables.utils.equiv_classes import EquivClasses
from NewAlgo.new_equiv_classes_generator import (
    ActionFunctionType,
    ActionsActionFunctionsMap,
    NewEquivClassGenerator,
)
from utils.type_definitions import ActionType


class NewActionsCayleyGenerator:
    """
    Generates a Cayley table for action compositions using the new algorithm.

    This class builds a complete action composition table by:
    1. Taking distinct actions and equivalence classes as input
    2. Computing compositions between actions using their action functions
    3. Finding which equivalence class contains each composed action

    The resulting table maps pairs of actions to their composition outcome.
    """

    def __init__(self) -> None:
        """Initialize the generator."""
        self.cayley_table_actions: CayleyTableActions

    def generate(self, equiv_classes_generator: NewEquivClassGenerator) -> None:
        """
        Generate the complete Cayley table for action compositions.

        Args:
            equiv_classes_generator: Generator containing distinct actions and their
                equivalence classes
        """
        print("\nGenerating actions Cayley table...")
        start_time = time.time()

        self.cayley_table_actions = CayleyTableActions()
        equiv_classes: EquivClasses = equiv_classes_generator.get_equiv_classes()
        equiv_classes_labels = equiv_classes.get_labels()
        distinct_actions: ActionsActionFunctionsMap = (
            equiv_classes_generator.get_distinct_actions()
        )

        self._generate_composition_table(equiv_classes_labels, distinct_actions)

        time_taken = time.time() - start_time
        print(f"\tActions Cayley table generated (Total taken: {time_taken:.2f}s)")

    def get_actions_cayley_table(self) -> CayleyTableActions:
        """Return the generated Cayley table for actions."""
        return self.cayley_table_actions

    def _generate_composition_table(
        self,
        equiv_classes_labels: list[ActionType],
        distinct_actions: ActionsActionFunctionsMap,
    ) -> None:
        """
        Generate the composition table entries.

        For each pair of actions (a,b), computes their composition by:
        1. Getting their action functions
        2. Composing the functions
        3. Finding which action has the composed function

        Args:
            equiv_classes_labels: Labels of equivalence classes to use as table indices
            distinct_actions: Collection of distinct actions and their functions
        """
        for right_action in equiv_classes_labels:
            self.cayley_table_actions.data[right_action] = {}
            for left_action in equiv_classes_labels:
                result = self._compute_composition(
                    left_action, right_action, distinct_actions
                )
                self.cayley_table_actions.data[right_action][left_action] = result

    def _compute_composition(
        self,
        left_action: ActionType,
        right_action: ActionType,
        distinct_actions: ActionsActionFunctionsMap,
    ) -> ActionType:
        """
        Compute a single composition of two actions.

        Args:
            left_action: The action applied second
            right_action: The action applied first
            distinct_actions: Collection of distinct actions and their functions

        Returns:
            The action that represents the composition result
        """
        # Get action_function for right_action and left_action.
        right_action_function = distinct_actions.get_action_function_from_action(
            right_action
        )
        left_action_function = distinct_actions.get_action_function_from_action(
            left_action
        )
        # Compose the action functions.
        composed_action_function = self._compose_action_functions(
            left_action_function, right_action_function
        )
        # Find action in distinct_actions that has the composed_action_function.
        composed_action = distinct_actions.get_action_from_action_function(
            composed_action_function
        )
        return composed_action

    def _compose_action_functions(
        self,
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
