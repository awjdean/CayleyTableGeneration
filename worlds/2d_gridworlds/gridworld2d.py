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
        self._grid_size = grid_shape
        self._minimum_actions = kwargs.get("minimum_actions", ["1", "W", "E", "N", "S"])

        # Generate possible states.
        self._possible_states = generate_states(grid_size=self._grid_size)

        # Check if initial state is valid
        initial_state = kwargs.get("initial_agent_state", (0, 0))
        if initial_state not in self._possible_states:
            raise ValueError("Initial state must be a valid state in the world")

        self._initial_state = initial_state


if __name__ == "__main__":
    grid = Gridworld2D(grid_shape=(2, 3), initial_agent_state=(1, 2))
    print(grid._possible_states)
