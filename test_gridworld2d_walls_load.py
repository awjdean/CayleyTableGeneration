from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls


def main():
    # Create a minimal instance (required for loading)
    grid_shape = (2, 3)
    wall_positions = []
    wall_strategy = "masked"

    gridworld = Gridworld2DWalls(grid_shape, wall_positions, wall_strategy)

    print("Before loading:")
    print(f"Wall Positions: {gridworld._wall_positions}")

    # Load the properties
    gridworld.load_world_properties("gridworld_properties.pkl")

    print("\nAfter loading:")
    print(f"Grid Shape: {gridworld._GRID_SHAPE}")
    print(f"Wall Positions: {gridworld._wall_positions}")
    print(f"Wall Strategy: {gridworld._wall_strategy}")
    print(f"Number of States: {len(gridworld._possible_states)}")


if __name__ == "__main__":
    main()
