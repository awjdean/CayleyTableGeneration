from type_definitions import ActionType, StateType
from worlds.gridworlds_2d.utils.move_objects_2d import MoveObject2DGrid

from ..base_world import BaseWorld
from .utils.generate_states import generate_states

GridPositionType = tuple[int, int]

TransformationMatrix = dict[GridPositionType, dict[ActionType, GridPositionType]]


class Gridworld2D(BaseWorld):
    def __init__(self, grid_shape: GridPositionType) -> None:
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

        self._GRID_SHAPE = grid_shape
        self._MIN_ACTIONS = ["1", "W", "E", "N", "S"]

        self._POSSIBLE_STATES = generate_states(grid_size=self._GRID_SHAPE)

    def get_possible_states(self) -> list[StateType]:
        return self._POSSIBLE_STATES

    def get_next_state(self, state, min_action):
        return MoveObject2DGrid(min_action).apply(
            object_position=state, grid_size=self._GRID_SHAPE
        )

    def plot(self):
        # TODO:
        # Initialise initial state for plotting.
        initial_state = (0, 0)
        if initial_state not in self._POSSIBLE_STATES:
            raise ValueError("Initial state must be a valid state in the world")
        self.set_state(state=initial_state)


if __name__ == "__main__":
    grid = Gridworld2D(grid_shape=(2, 3))
    print(grid._POSSIBLE_STATES)
    # print(make_world_cyclical(object_position=(0, 0), grid_size=(2, 3)))
