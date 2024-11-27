from enum import Enum

from ..base_world import BaseWorld
from .generate_states import generate_states


class Gridworld2D(BaseWorld):
    def __init__(self, grid_shape: tuple[int, int], **kwargs) -> None:
        """Initialize a 2D grid world.

        Args:
            grid_shape: Tuple of (max_x, max_y) defining maximum grid coordinates
            **kwargs: Optional keyword arguments
                minimum_actions: List of possible actions (default: ["1", "W", "E", "N", "S"])
                initial_agent_position: Starting position as (x, y) tuple (default: (0, 0))
        """
        super().__init__()

        if not all(isinstance(x, int) and x > 0 for x in grid_shape):
            raise ValueError("Grid dimensions must be positive integers")
        self._grid_shape = grid_shape
        self._min_actions = kwargs.get("minimum_actions", ["1", "W", "E", "N", "S"])

        # Generate possible states.
        self._possible_states = generate_states(grid_size=self._grid_shape)

        # Check if initial state is valid
        initial_state = kwargs.get("initial_agent_state", (0, 0))
        if initial_state not in self._possible_states:
            raise ValueError("Initial state must be a valid state in the world")

        self._initial_state = initial_state

    def generate_min_action_transformation_matrix(self):
        tranformation_matrix = {}
        for initial_state in self._possible_states:
            tranformation_matrix[initial_state] = {}
            for action in self._min_actions:
                final_state = MoveObject2DGrid(action).apply(
                    object_position=initial_state, grid_size=self._grid_shape
                )
                tranformation_matrix[initial_state][action] = final_state
        self._minimum_action_transformation_matrix = tranformation_matrix


class MoveObject2DGrid(Enum):
    """
    Moves objects in a 2D grid world.
    """

    NOOP = "1"
    LEFT = "W"
    RIGHT = "E"
    UP = "N"
    DOWN = "S"

    def apply(self, object_position, grid_size):
        if self == self.NOOP:
            return object_position
        elif self == self.LEFT:
            object_position = object_position[0] - 1, object_position[1]
        elif self == self.RIGHT:
            object_position = object_position[0] + 1, object_position[1]
        elif self == self.UP:
            object_position = object_position[0], object_position[1] + 1
        elif self == self.DOWN:
            object_position = object_position[0], object_position[1] - 1

        object_position = make_world_cyclical(
            object_position=object_position, grid_size=grid_size
        )
        return object_position


def make_world_cyclical(object_position, grid_size):
    """
    Converts positions of objects that are out of the grid size to the relevant cyclical
     positions.
    """
    return tuple(object_position[i] % grid_size[i] for i in range(len(grid_size)))


if __name__ == "__main__":
    grid = Gridworld2D(grid_shape=(2, 3), initial_agent_state=(1, 2))
    print(grid._possible_states)
    # print(make_world_cyclical(object_position=(0, 0), grid_size=(2, 3)))
