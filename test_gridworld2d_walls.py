from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls


def main():
    # Create a 3x3 grid with some walls
    grid_shape = (3, 3)
    wall_positions = [(0.0, 0.5), (1.0, 0.5)]
    wall_strategy = "identity"

    # Create the world
    world = Gridworld2DWalls(
        grid_shape=grid_shape,
        wall_positions=wall_positions,
        wall_strategy=wall_strategy,
    )

    # Generate the transformation matrix (needed for drawing)
    world.generate_min_action_transformation_matrix()

    # Draw the graph
    world.draw_graph(
        include_undefined_state=False,
        show_edge_labels=False,
        show_legend=True,
        layout_engine="fdp",
    )


if __name__ == "__main__":
    main()
