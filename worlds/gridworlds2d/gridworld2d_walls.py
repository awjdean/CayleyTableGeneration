from undefined_action_strat import UndefinedActionStrat
from utils.type_definitions import ActionType, StateType
from worlds.gridworlds2d.gridworld2d import GridPosition2DType, Gridworld2D
from worlds.gridworlds2d.utils.make_world_cyclical import make_world_cyclical
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid

WallPositionsType = list[tuple[float, float]]

# Define constant for wall position relative to states.
HALF_INT = 0.5


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

        check_walls(wall_positions, grid_shape)
        pseudo_wall_positions = generate_cyclical_pseudo_wall_positions(
            wall_positions, grid_shape
        )

        self._wall_positions = wall_positions + pseudo_wall_positions

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        agent_position = state

        agent_moving_into_wall = self._is_object_moving_into_wall(
            object_position=agent_position,
            wall_positions=self._wall_positions,
            min_action=min_action,
        )
        if agent_moving_into_wall:
            # TODO: test this.
            return UndefinedActionStrat(self._wall_strategy).apply(state)
        else:
            return MoveObject2DGrid(min_action).apply(
                object_position=state, grid_shape=self._GRID_SHAPE
            )

    def _is_object_moving_into_wall(
        self,
        object_position: GridPosition2DType,
        wall_positions: WallPositionsType,
        min_action: ActionType,
    ) -> bool:
        if min_action == "1":
            return False
        # Moving up into wall.
        elif min_action == "N":
            x_change = 0.0
            y_change = HALF_INT
        # Moving down into wall.
        elif min_action == "S":
            x_change = 0.0
            y_change = -HALF_INT
        # Moving right into wall.
        elif min_action == "E":
            x_change = HALF_INT
            y_change = 0.0
        # Moving left into wall.
        elif min_action == "W":
            x_change = -HALF_INT
            y_change = 0.0
        else:
            raise Exception(f"Minimum action not in {self._MIN_ACTIONS}")

        return self._is_wall_at_position(
            object_position=object_position,
            wall_positions=wall_positions,
            x_change=x_change,
            y_change=y_change,
        )

    def draw(self):
        # TODO: use draw from GridWorld2D, then draw in walls.
        pass

    def _is_wall_at_position(
        self,
        object_position: GridPosition2DType,
        wall_positions: WallPositionsType,
        x_change: float,
        y_change: float,
    ):
        for wall_position in wall_positions:
            possible_wall_position_that_object_traverses = (
                object_position[0] + x_change,
                object_position[1] + y_change,
            )
            if wall_position == possible_wall_position_that_object_traverses:
                return True
            # Enforcing cyclical world.
            if wall_position == make_world_cyclical(
                possible_wall_position_that_object_traverses, self._GRID_SHAPE
            ):
                return True
        return False


def check_walls(
    wall_positions: WallPositionsType, grid_shape: GridPosition2DType
) -> None:
    max_x = grid_shape[0]
    max_y = grid_shape[1]
    for wall_position in wall_positions:
        # Check x and y position ranges
        if not (-HALF_INT <= wall_position[0] <= max_x - HALF_INT):
            raise ValueError(
                f"Invalid x position: {wall_position[0]}."
                f" Must be in range [-{HALF_INT}, {max_x - HALF_INT}]."
            )
        if not (-HALF_INT <= wall_position[1] <= max_y - HALF_INT):
            raise ValueError(
                f"Invalid y position: {wall_position[1]}."
                f" Must be in range [-{HALF_INT}, {max_y - HALF_INT}]."
            )

        # Existing validation for position types
        if not (
            (
                (
                    isinstance(wall_position[0], int | float)
                    and wall_position[0] % 1 == 0
                )
                and (
                    isinstance(wall_position[1], int | float)
                    and wall_position[1] % 1 == HALF_INT
                )
            )
            or (
                isinstance(wall_position[1], int | float)
                and wall_position[1] % 1 == 0
                and isinstance(wall_position[0], int | float)
                and wall_position[0] % 1 == HALF_INT
            )
        ):
            raise ValueError(
                f"Invalid wall position: {wall_position}. "
                "Must be (int, half int) or (half int, int)."
            )


def generate_cyclical_pseudo_wall_positions(
    wall_positions: WallPositionsType, grid_shape: GridPosition2DType
) -> WallPositionsType:
    """
    Creates extra 'pseudo' walls that exhibit the cyclical behaviour of the world.
    """
    cyclical_pseudo_walls = []
    max_x, max_y = grid_shape

    for wall_position in wall_positions:
        x, y = wall_position

        # Check and create cyclical pseudo walls based on the given conditions
        if x == -HALF_INT:
            cyclical_pseudo_walls.append((max_x - HALF_INT, y))
        elif x == max_x - HALF_INT:
            cyclical_pseudo_walls.append((-HALF_INT, y))
        elif y == -HALF_INT:
            cyclical_pseudo_walls.append((x, max_y - HALF_INT))
        elif y == max_y - HALF_INT:
            cyclical_pseudo_walls.append((x, -HALF_INT))

    return cyclical_pseudo_walls
