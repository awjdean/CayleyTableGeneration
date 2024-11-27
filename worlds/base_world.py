"""
Features present in any world class.
"""

from abc import abstractmethod
from typing import Any


class BaseWorld:
    def __init__(self) -> None:
        self._current_state: Any | None = None
        self._minimum_actions: list[Any] = []
        self._minimum_action_transformation_matrix: dict[Any, dict[Any, Any]] | None = (
            None
        )
        self._initial_state: Any | None = None
        self._possible_states: list[Any] = []

    def get_state(self) -> Any | None:
        return self._current_state

    def reset_state(self) -> None:
        self._current_state = self._initial_state

    @abstractmethod
    def get_possible_states(self) -> list[Any]:
        raise NotImplementedError("Subclasses must implement get_possible_states.")

    @abstractmethod
    def generate_min_action_transformation_matrix(self) -> dict[Any, dict[Any, Any]]:
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
