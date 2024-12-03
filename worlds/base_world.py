"""
Features present in any world class.
"""

from abc import abstractmethod

from type_definitions import ActionType, MinActionsType, StateType, TransformationMatrix


class BaseWorld:
    def __init__(self) -> None:
        self._current_state: StateType
        self._MIN_ACTIONS: list[str] = []
        self._minimum_action_transformation_matrix: TransformationMatrix = {}
        self._POSSIBLE_STATES: list[StateType] = []

    @abstractmethod
    def get_possible_states(self) -> list[StateType]:
        raise NotImplementedError("Subclasses must implement get_possible_states.")

    @abstractmethod
    def get_next_state(
        self, initial_state: StateType, min_action: ActionType
    ) -> StateType:
        raise NotImplementedError(
            "Subclasses must implement generate_min_action_transformation_matrix."
        )

    def get_state(self) -> StateType:
        return self._current_state

    def set_state(self, state: StateType) -> None:
        if state not in self._POSSIBLE_STATES:
            raise ValueError(
                f"Invalid state: {state}. State must be one of {self._POSSIBLE_STATES}"
            )
        self._current_state = state

    def generate_min_action_transformation_matrix(self) -> None:
        """Generate the transformation matrix for all possible state-action pairs."""
        if self._minimum_action_transformation_matrix:
            print("Transformation matrix already exists.")
        elif not self._POSSIBLE_STATES:
            raise ValueError("Possible states are not defined.")
        elif not self._MIN_ACTIONS:
            raise ValueError("Minimum actions are not defined.")
        else:
            transformation_matrix: TransformationMatrix = {}
            for state in self._POSSIBLE_STATES:
                transformation_matrix[state] = {}
                for min_action in self._MIN_ACTIONS:
                    transformation_matrix[state][min_action] = self.get_next_state(
                        state, min_action
                    )
            self._minimum_action_transformation_matrix = transformation_matrix

    def _apply_min_action(self, min_action: ActionType) -> None:
        """
        Lookup a precomputed state-action pair in the transformation matrix.
        """
        if self._minimum_action_transformation_matrix is None:
            raise ValueError("Minimum action transformation matrix is not defined.")
        try:
            self._current_state = self._minimum_action_transformation_matrix[
                self._current_state
            ][min_action]
        except KeyError:
            raise ValueError(
                f"Invalid state-action pair: {self._current_state}-{min_action}"
            )

    def apply_action_sequence(self, action_sequence: ActionType) -> None:
        """
        # TODO: build in a check here so that if action goes to the undefined state,
        #  we can skip the rest of the look ups.
        """
        for min_action in action_sequence[::-1]:
            self._apply_min_action(min_action)

    def get_min_actions(self) -> MinActionsType:
        return self._MIN_ACTIONS

    def save_minimum_action_transformation_matrix(self, path: str) -> None:
        """
        From minimum_action_transformation_matrix we can extract minimum actions,
          and states.
        """
        pass

    def load_minimum_action_transformation_matrix(self, path: str) -> None:
        """
        Load minimum action transformation matrix from a file.
        # TODO: Load minimum actions, states, and transformation matrix; ask user to
        #  input initial_state?
        """
        pass
