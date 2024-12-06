def make_world_cyclical(
    position: tuple[int | float, ...],  # TODO: CHECK
    grid_shape: tuple[int, ...],
):
    """
    Converts positions of objects that are out of the grid size to the relevant cyclical
     positions.
    """
    return tuple(position[i] % grid_shape[i] for i in range(len(grid_shape)))
