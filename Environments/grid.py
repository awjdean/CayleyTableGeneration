from enum import Enum
from itertools import product
from typing import NamedTuple, Tuple, List, Set

class Action(Enum):
    NOOP = "1"
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"


class Position2D(NamedTuple):
    x: int
    y: int


class WallPosition(NamedTuple):
    x: float
    y: float


_position = types.NamedUniTuple(types.int64, 2, Position2D)
_transition_map = types.DictType(Action, _position)


_kv_type = (_position, _transition_map)


class TransitionGrid:
    def __init__(self):
        self.grid = typed.Dict.empty(*_kv_type)


def generate_transition_grid(
    grid_size: Tuple[int, int],
    wall_positions: Set[Position2D],
) -> TransitionGrid:
    def _wrap(x, y) -> Position2D:
        return Position2D(x, y)

    def _get_next_position(position: Position2D, action: Action) -> bool:
        if action == Action.NOOP:
            return position
        elif action == Action.UP:
            if WallPosition(position.x, position.y + 0.5) in wall_positions:
                return position
            return _wrap(position.x, position.y + 1)
        elif action == Action.DOWN:
            if WallPosition(position.x, position.y - 0.5) in wall_positions:
                return position
            return _wrap(position.x, position.y - 1)
        elif action == Action.LEFT:
            if WallPosition(position.x - 0.5, position.y) in wall_positions:
                return position
            return _wrap(position.x - 1, position.y)
        elif action == Action.RIGHT:
            if WallPosition(position.x + 0.5, position.y) in wall_positions:
                return position
            return _wrap(position.x + 1, position.y)

    def _generate_transition_map(position: Position2D):
        transition_map = typed.Dict.empty(Action, _position)
        for action in Action:
            transition_map[action] = _get_next_position(position, action)
        return transition_map

    grid = TransitionGrid()
    for i, j in product(range(grid_size[0]), range(grid_size[1])):
        pos = Position2D(i, j)
        grid[pos] = _generate_transition_map(pos)

    return grid
