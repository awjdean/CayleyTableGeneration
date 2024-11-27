"""
Features present in any world class.
"""

from abc import abstractmethod


class BaseWorld:
    def __init__(self) -> None:
        self.current_state = None
        self.minimum_actions = None
        self.minimum_action_transformation_matrix = None
        self.initial_state = None
        self.possible_states = None

    def get_state(self) -> None:
        return self.current_state

    def reset_state(self) -> None:
        self.current_state = self.initial_state

    @abstractmethod
    def get_possible_states(self) -> list:
        raise NotImplementedError("Subclasses must implement get_possible_states.")

    @abstractmethod
    def create_minimum_action_transformation_matrix(self) -> dict:
        raise NotImplementedError(
            "Subclasses must implement create_minimum_action_transformation_matrix."
        )

    def apply_minimum_action(self, action: str) -> None:
        """
        Lookup a precomputed state-action pair in the transformation matrix.
        """
        if self.minimum_action_transformation_matrix is None:
            raise ValueError("Minimum action transformation matrix is not defined.")
        try:
            self._current_state = self.minimum_action_transformation_matrix[
                self.current_state
            ][action]
        except KeyError:
            raise ValueError(
                f"Invalid state-action pair: {self.current_state}-{action}"
            )

    def apply_action(self) -> None:
        """
        # TODO: build in a check here so that if action goes to the undefined state, we can skip the rest of the look ups.
        """
        pass

    def save_minimum_action_transformation_matrix(self, path: str) -> None:
        """
        From minimum_action_transformation_matrix we can extract minimum actions, and states.
        """
        pass

    def load_minimum_action_transformation_matrix(self, path: str) -> None:
        """
        Load minimum action transformation matrix from a file.
        # TODO: Load minimum actions, states, and transformation matrix; ask user to input initial_state?
        """
        pass
