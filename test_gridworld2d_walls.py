from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls


def main():
    # Define grid shape and wall positions
    grid_shape = (2, 3)  # Example grid size
    wall_positions = [(0.5, 1), (1, 1.5)]  # Example wall positions
    wall_strategy = "masked"  # Example wall strategy

    # Create an instance of Gridworld2DWalls
    gridworld = Gridworld2DWalls(grid_shape, wall_positions, wall_strategy)

    # Generate the transformation matrix
    gridworld.generate_min_action_transformation_matrix()

    # Print before saving
    print("Before saving:")
    print(f"Wall Positions: {gridworld._wall_positions}")

    # Save the properties of the instance
    gridworld.save_world_properties("gridworld_properties.pkl")


if __name__ == "__main__":
    main()
