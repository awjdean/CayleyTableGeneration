"""
Provides functionality for moving objects in a 2D grid world environment.

This module contains utilities for handling movement operations in a 2D grid,
including directional movements (left, right, up, down) and no-operation (NOOP).
All movements are handled in a cyclical manner, meaning objects wrap around the
grid boundaries.
"""

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

    def apply(
        self, object_position: GridPosition2DType, grid_shape: tuple[int, int]
    ) -> GridPosition2DType:
        """
        Apply the movement direction to the given object position.

        Parameters:
        - object_position (GridPosition2DType): The current position of the object.
        - grid_shape (tuple[int, int]): The shape of the grid (width, height).

        Returns:
        - GridPosition2DType: The new position of the object after movement.
        """
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
