"""
Features present in any world class.
"""

from abc import abstractmethod

from utils.type_definitions import (
    ActionType,
    MinActionsType,
    StateType,
    TransformationMatrix,
)
from worlds.utils.undefined_state import UndefinedStates


class BaseWorld:
    def __init__(self, min_actions) -> None:
        self._current_state: StateType
        self._MIN_ACTIONS: list[ActionType] = min_actions
        self._minimum_action_transformation_matrix: TransformationMatrix = {}
        self._possible_states: list[StateType] = []

    @abstractmethod
    def generate_possible_states(self) -> list[StateType]:
        """Return a list of possible states for the world."""
        raise NotImplementedError("Subclasses must implement generate_possible_states.")

    @abstractmethod
    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        """Return the next state given the current state and a minimum action."""
        raise NotImplementedError("Subclasses must implement get_next_state.")

    def get_state(self) -> StateType:
        return self._current_state

    def set_state(self, state: StateType) -> None:
        """Set the current state of the world.

        Args:
            state (StateType): The state to set as the current state.

        Raises:
            ValueError: If the state is not in the list of possible states.
        """
        possible_states = self.get_possible_states()
        if state not in possible_states:
            raise ValueError(
                f"Invalid state: {state}. " f"State must be one of {possible_states}."
            )
        self._current_state = state

    def get_possible_states(self) -> list[StateType]:
        if not self._possible_states:
            print("\tGenerating possible states.")
            self._possible_states = self.generate_possible_states()
        return self._possible_states

    def generate_min_action_transformation_matrix(self) -> None:
        """Generate the transformation matrix for all possible state-action pairs.

        Raises:
            ValueError: If possible states or minimum actions are not defined.
        """
        if self._minimum_action_transformation_matrix:
            print("Transformation matrix already exists.")
        elif not self._MIN_ACTIONS:
            raise ValueError("Minimum actions are not defined.")
        else:
            self._add_undefined_state_to_possible_states()
            transformation_matrix: TransformationMatrix = {}
            for state in self.get_possible_states():
                transformation_matrix[state] = {}
                for min_action in self._MIN_ACTIONS:
                    # Undefined state is absorbing.
                    if state == (None,):
                        next_state = (None,)
                    else:
                        next_state = self.get_next_state(state, min_action)
                    transformation_matrix[state][min_action] = next_state
            self._minimum_action_transformation_matrix = transformation_matrix

    def _add_undefined_state_to_possible_states(self) -> None:
        """
        Add the undefined state to the list of possible states if it is not already
         present.
        """
        undefined_state = UndefinedStates.BASIC.value
        if undefined_state not in self.get_possible_states():
            self._possible_states.append(undefined_state)

    def _apply_min_action(self, min_action: ActionType) -> None:
        """Lookup a precomputed state-action pair in the transformation matrix.

        Args:
            min_action (ActionType): The minimum action to apply.

        Raises:
            ValueError: If the minimum action transformation matrix is not defined or if
            the state-action pair is invalid.
        """
        if self._minimum_action_transformation_matrix is None:
            raise ValueError("Minimum action transformation matrix is not defined.")

        if self._current_state not in self._minimum_action_transformation_matrix:
            raise ValueError(
                f"Current state {self._current_state} is not valid in the"
                " transformation matrix."
            )

        try:
            self._current_state = self._minimum_action_transformation_matrix[
                self._current_state
            ][min_action]
        except KeyError:
            raise ValueError(
                f"Invalid state-action pair: {self._current_state}-{min_action}. "
                f"Check if the action is valid for the current state."
            )

    def apply_action_sequence(self, action_sequence: ActionType) -> None:
        """Apply a sequence of actions in reverse order.

        Args:
            action_sequence (ActionType): The sequence of actions to apply.

        # TODO: Build in a check here so that if action goes to the undefined state, we
        #  can skip the rest of the lookups.
        """
        for min_action in action_sequence[::-1]:
            self._apply_min_action(min_action)

    def get_min_actions(self) -> MinActionsType:
        return self._MIN_ACTIONS

    def save_minimum_action_transformation_matrix(self, path: str) -> None:
        """Save the minimum action transformation matrix to a file.

        Args:
            path (str): The file path to save the transformation matrix.
        """
        pass

    def load_minimum_action_transformation_matrix(self, path: str) -> None:
        """Load the minimum action transformation matrix from a file.

        Args:
            path (str): The file path to load the transformation matrix from.

        # TODO: Load minimum actions, states, and transformation matrix; ask user to
        # input initial_state?
        """
        pass
