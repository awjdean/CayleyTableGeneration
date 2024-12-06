from enum import Enum

from utils.type_definitions import GridPosition2DType
from worlds.gridworlds2d.utils.make_world_cyclical import make_world_cyclical


class MoveObject2DGrid(Enum):
    """
    Moves objects in a 2D grid world.
    """

    NOOP = "1"
    LEFT = "W"
    RIGHT = "E"
    UP = "N"
    DOWN = "S"

    def apply(self, object_position: GridPosition2DType, grid_shape: tuple[int, ...]):
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
            position=object_position, grid_shape=grid_shape
        )
        return object_position
