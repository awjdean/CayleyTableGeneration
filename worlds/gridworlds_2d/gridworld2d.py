from worlds.gridworlds_2d.utils.move_objects_2d import MoveObject2DGrid

from ..base_world import BaseWorld
from .utils.generate_states import generate_states

GridPosition = tuple[int, int]
ActionType = str
TransformationMatrix = dict[GridPosition, dict[ActionType, GridPosition]]


class Gridworld2D(BaseWorld):
    def __init__(self, grid_shape: GridPosition, **kwargs) -> None:
        """Initialize a 2D grid world.

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
        super().__init__()

        if not all(isinstance(x, int) and x > 0 for x in grid_shape):
            raise ValueError("Grid dimensions must be positive integers")

        self._grid_shape = grid_shape
        self._min_actions = kwargs.get("minimum_actions", ["1", "W", "E", "N", "S"])
        self._possible_states = generate_states(grid_size=self._grid_shape)

        initial_state = kwargs.get("initial_agent_state", (0, 0))
        if initial_state not in self._possible_states:
            raise ValueError("Initial state must be a valid state in the world")

        self._initial_state = initial_state

    def get_next_state(self, initial_state, min_action):
        return MoveObject2DGrid(min_action).apply(
            object_position=initial_state, grid_size=self._grid_shape
        )


if __name__ == "__main__":
    grid = Gridworld2D(grid_shape=(2, 3), initial_agent_state=(1, 2))
    print(grid._possible_states)
    # print(make_world_cyclical(object_position=(0, 0), grid_size=(2, 3)))
