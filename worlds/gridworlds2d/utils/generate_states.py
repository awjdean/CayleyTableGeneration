import itertools


def generate_states(grid_size: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Creates a list of all possible states in a 2D grid.

    Args:
        grid_size: A tuple of (max_x, max_y) defining maximum grid coordinates

    Returns:
        A list of (x, y) tuples representing all possible positions in the grid

    Raises:
        ValueError: If grid dimensions are not positive integers
    """
    if not all(isinstance(x, int) and x > 0 for x in grid_size):
        raise ValueError("Grid dimensions must be positive integers")

    return [
        (i, j) for i, j in itertools.product(range(grid_size[0]), range(grid_size[1]))
    ]
