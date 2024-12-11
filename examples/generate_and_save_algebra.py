import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.transformation_algebra import TransformationAlgebra
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls


def main():
    # Create a simple gridworld with walls
    world = Gridworld2DWalls(
        grid_shape=(2, 2),
        wall_positions=[(0.5, 0)],  # Wall between (0,0) and (1,0)
        wall_strategy="identity",
    )
    world.generate_min_action_transformation_matrix()

    # Create initial state (starting position)
    initial_state = (0, 0)

    # Create and name the transformation algebra
    algebra = TransformationAlgebra(name="gridworld_2x2_wall")

    # Generate the Cayley tables and equivalence classes
    print("Generating Cayley table states...")
    algebra.generate_cayley_table_states(world=world, initial_state=initial_state)

    print("Generating Cayley table actions...")
    algebra.generate_cayley_table_actions()

    # Save the algebra
    print("Saving algebra...")
    algebra.save(path=None)  # Will save to ./saved/algebra/gridworld_2x2_wall.pkl

    print("\nGenerated tables:")
    print(algebra.cayley_table_states)
    print(algebra.cayley_table_actions)
    print("\nSaved to: ./saved/algebra/gridworld_2x2_wall.pkl")


if __name__ == "__main__":
    main()
