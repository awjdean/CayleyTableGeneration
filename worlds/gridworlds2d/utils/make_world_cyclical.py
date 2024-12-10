from typing import TypeVar

T = TypeVar("T", int, float)


def make_world_cyclical(
    position: tuple[T, T],
    grid_shape: tuple[int, int],
) -> tuple[T, T]:
    """
    Converts positions of objects that are out of the grid size to the relevant cyclical
     positions.

    Args:
        position (tuple[T, T]): The (x, y) coordinates of the position.
        grid_shape (tuple[int, int]): The dimensions of the grid (width, height).

    Returns:
        tuple[T, T]: The adjusted (x, y) coordinates within the grid.
    """
    return (position[0] % grid_shape[0], position[1] % grid_shape[1])
