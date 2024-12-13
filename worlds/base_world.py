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
from worlds.world_saver import WorldSaver


class BaseWorld:
    def __init__(self, min_actions) -> None:
        self._current_state: StateType
        self._MIN_ACTIONS: list[ActionType] = min_actions
        self._min_action_transformation_matrix: TransformationMatrix = {}
        self._possible_states: list[StateType] = []
        self.world_saver = WorldSaver()

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
        if self._min_action_transformation_matrix:
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
                    if state == UndefinedStates.BASIC.value:
                        next_state = UndefinedStates.BASIC.value
                    else:
                        next_state = self.get_next_state(state, min_action)
                    transformation_matrix[state][min_action] = next_state
            self._min_action_transformation_matrix = transformation_matrix

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
        if self._min_action_transformation_matrix is None:
            raise ValueError("Minimum action transformation matrix is not defined.")

        if self._current_state not in self._min_action_transformation_matrix:
            raise ValueError(
                f"Current state {self._current_state} is not valid in the"
                " transformation matrix."
            )

        try:
            self._current_state = self._min_action_transformation_matrix[
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

    def save_world_properties(self, path: str) -> None:
        """Save the world properties to a JSON file."""
        properties = self._get_world_properties_for_save()
        self.world_saver.save_world_properties(properties, path)

    def load_world_properties(self, path: str) -> None:
        """Load the world properties from a pickle file."""
        # Get the keys of additional properties that need to be loaded
        additional_properties_keys = set(
            self._get_additional_properties_for_save().keys()
        )

        # Load properties using WorldSaver
        properties = self.world_saver.load_world_properties(
            path, additional_properties_keys
        )

        # Set the properties
        self._MIN_ACTIONS = properties["minimum_actions"]
        self._possible_states = properties["possible_states"]
        self._min_action_transformation_matrix = properties[
            "min_action_transformation_matrix"
        ]

        # Set additional properties
        for key, value in properties.items():
            if key not in [
                "minimum_actions",
                "possible_states",
                "min_action_transformation_matrix",
            ]:
                setattr(self, f"_{key.upper()}", value)

    def _get_world_properties_for_save(self) -> dict:
        """Collect all relevant world properties into a dictionary.

        Returns:
            dict: Dictionary containing world properties including minimum actions,
                 possible states, and transformation matrix.
        """
        return {
            "minimum_actions": self._MIN_ACTIONS,
            "possible_states": self._possible_states,
            "min_action_transformation_matrix": self._min_action_transformation_matrix,
            **self._get_additional_properties_for_save(),
        }

    def _get_additional_properties_for_save(self) -> dict:
        """Get additional properties specific to the world subclass.

        Returns:
            dict: Additional properties to save. Empty by default.
        """
        return {}
