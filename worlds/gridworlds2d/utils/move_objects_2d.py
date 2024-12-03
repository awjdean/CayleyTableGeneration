from enum import Enum


class MoveObject2DGrid(Enum):
    """
    Moves objects in a 2D grid world.
    """

    NOOP = "1"
    LEFT = "W"
    RIGHT = "E"
    UP = "N"
    DOWN = "S"

    def apply(self, object_position, grid_shape):
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
            object_position=object_position, grid_shape=grid_shape
        )
        return object_position


def make_world_cyclical(object_position, grid_shape):
    """
    Converts positions of objects that are out of the grid size to the relevant cyclical
     positions.
    """
    return tuple(object_position[i] % grid_shape[i] for i in range(len(grid_shape)))
