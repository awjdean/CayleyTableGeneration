from utils.type_definitions import GridPosition2DType, StateType
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid

from ..base_world import BaseWorld
from .utils.generate_2d_grid_positions import generate_2d_grid_positions


class Gridworld2D(BaseWorld):
    def __init__(self, grid_shape: GridPosition2DType) -> None:
        """
        Initialize a 2D grid world.
        State has one-to-one correspondence to position of the agent.

        Args:
            grid_shape: Tuple of (max_x, max_y) defining maximum grid coordinates
            **kwargs: Optional keyword arguments
                minimum_actions: List of possible actions
                  (default: ["1", "W", "E", "N", "S"])
                initial_agent_state: Starting position as (x, y) tuple (default: (0, 0))

        Raises:
            ValueError: If grid dimensions are not positive integers or initial state is
              invalid
        """
        min_actions = ["1", "W", "E", "N", "S"]
        super().__init__(min_actions)

        if not all(isinstance(x, int) and x > 0 for x in grid_shape):
            raise ValueError("Grid dimensions must be positive integers")
        self._GRID_SHAPE = grid_shape

    def generate_possible_states(self) -> list[StateType]:
        possible_states = generate_2d_grid_positions(grid_size=self._GRID_SHAPE)
        return possible_states

    def get_next_state(self, state, min_action):
        return MoveObject2DGrid(min_action).apply(
            object_position=state, grid_shape=self._GRID_SHAPE
        )

    def draw(self):
        # TODO: Implement this.
        pass


if __name__ == "__main__":
    grid = Gridworld2D(grid_shape=(2, 3))
    grid.generate_min_action_transformation_matrix()
    print(grid.get_possible_states())
