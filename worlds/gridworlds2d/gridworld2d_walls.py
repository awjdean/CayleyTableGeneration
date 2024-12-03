from utils.type_definitions import ActionType, StateType
from worlds.gridworlds2d.gridworld2d import GridPosition2DType, Gridworld2D
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid

WallPositionsType = list[GridPosition2DType]


class Gridworld2DWalls(Gridworld2D):
    def __init__(
        self,
        grid_shape: GridPosition2DType,
        wall_positions: WallPositionsType,
        wall_strategy: str,
    ):
        super().__init__(grid_shape)
        if wall_strategy not in ["identity", "masked"]:
            raise ValueError("wall_strategy must be either 'identity' or 'masked'")

        self._wall_strategy = wall_strategy
        self._wall_positions = wall_positions

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        # Check if wall in way.
        agent_position = state
        agent_moving_into_wall = self._check_if_object_moving_into_wall(
            object_position=agent_position,
            wall_positions=self._wall_positions,
            min_action=min_action,
        )
        if agent_moving_into_wall:
            if self._wall_strategy == "identity":
                return agent_position
            if self._wall_strategy == "masked":
                return (None, None)
            else:
                raise ValueError(
                    "Invalid wall strategy: '{self._wall_strategy}'"
                    "Must be either 'identity' or 'masked'."
                )
        else:
            return MoveObject2DGrid(min_action).apply(
                object_position=state, grid_shape=self._GRID_SHAPE
            )

    def draw(self):
        # TODO: use draw from GridWorld2D, then draw in walls.
        pass

    def _check_if_object_moving_into_wall(
        self,
        object_position: GridPosition2DType,
        wall_positions: WallPositionsType,
        min_action: ActionType,
    ) -> bool:
        if min_action == "1":
            return False
        # Moving up into wall.
        # TODO: check.
        elif min_action == "N":
            x_change = 0.0
            y_change = 0.5
        # Moving down into wall.
        # TODO: check.
        elif min_action == "S":
            x_change = 0.0
            y_change = -0.5
        # Moving right into wall.
        # TODO: check.
        elif min_action == "E":
            x_change = 0.5
            y_change = 0.0
        # Moving left into wall.
        # TODO: check.
        elif min_action == "W":
            x_change = -0.5
            y_change = 0.0
        else:
            raise Exception(f"Minimum action not in {self._MIN_ACTIONS}")

        return is_wall_at_position(
            object_position=object_position,
            wall_positions=wall_positions,
            x_change=x_change,
            y_change=y_change,
        )


def is_wall_at_position(
    object_position: GridPosition2DType,
    wall_positions: WallPositionsType,
    x_change: float,
    y_change: float,
):
    for wall_position in wall_positions:
        if wall_position == (
            object_position[0] + x_change,
            object_position[1] + y_change,
        ):
            return True
    return False


def check_walls_in_grid():
    pass
