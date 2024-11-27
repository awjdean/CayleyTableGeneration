"""
Features present in any world class.
"""

from abc import abstractmethod
from typing import Any

TransformationMatrix = dict[Any, dict[Any, Any]]


class BaseWorld:
    def __init__(self) -> None:
        self._current_state: Any | None = None
        self._min_actions: list[Any] | None = None
        self._minimum_action_transformation_matrix: TransformationMatrix | None = None
        self._initial_state: Any | None = None
        self._possible_states: list[Any] | None = None

    def get_state(self) -> Any | None:
        return self._current_state

    def reset_state(self) -> None:
        self._current_state = self._initial_state

    @abstractmethod
    def get_possible_states(self) -> list[Any]:
        raise NotImplementedError("Subclasses must implement get_possible_states.")

    def generate_min_action_transformation_matrix(self) -> None:
        """Generate the transformation matrix for all possible state-action pairs."""
        if self._minimum_action_transformation_matrix is not None:
            print("Transformation matrix already exists.")
        elif self._possible_states is None:
            raise ValueError("Possible states are not defined.")
        elif self._min_actions is None:
            raise ValueError("Minimum actions are not defined.")
        else:
            transformation_matrix: TransformationMatrix = {}
            for initial_state in self._possible_states:
                transformation_matrix[initial_state] = {}
                for min_action in self._min_actions:
                    transformation_matrix[initial_state][min_action] = (
                        self.get_next_state(initial_state, min_action)
                    )
            self._minimum_action_transformation_matrix = transformation_matrix

    @abstractmethod
    def get_next_state(self, initial_state: Any, min_action: Any) -> Any:
        raise NotImplementedError(
            "Subclasses must implement generate_min_action_transformation_matrix."
        )

    def apply_minimum_action(self, action: str) -> None:
        """
        Lookup a precomputed state-action pair in the transformation matrix.
        """
        if self._minimum_action_transformation_matrix is None:
            raise ValueError("Minimum action transformation matrix is not defined.")
        try:
            self._current_state = self._minimum_action_transformation_matrix[
                self._current_state
            ][action]
        except KeyError:
            raise ValueError(
                f"Invalid state-action pair: {self._current_state}-{action}"
            )

    def apply_action(self) -> None:
        """
        # TODO: build in a check here so that if action goes to the undefined state,
        #  we can skip the rest of the look ups.
        """
        pass

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
