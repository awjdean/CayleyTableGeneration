import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


from transformation_algebra.transformation_algebra import TransformationAlgebra
from transformation_algebra.utils.algebra_generation_methods import (
    AlgebraGenerationMethod,
)
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls


def main():
    # Create and setup world
    world = Gridworld2DWalls(
        grid_shape=(2, 2),
        wall_positions=[(0.5, 0)],
        wall_strategy="identity",
    )
    world.generate_min_action_transformation_matrix()

    # Generate algebra
    algebra = TransformationAlgebra(name="gridworld2D_walls")
    algebra.generate(
        world=world,
        initial_state=(0, 0),
        method=AlgebraGenerationMethod.STATES_CAYLEY,
    )

    # Print algebra information
    print("States Cayley Table:")
    print(algebra.cayley_table_states)
    print("\nEquivalence Classes:")
    print(algebra.equiv_classes)
    print("\nActions Cayley Table:")
    print(algebra.cayley_table_actions)

    # Visualize the world
    world.draw_graph(
        include_undefined_state=True,
        show_edge_labels=True,
        save_path="gridworld2d_walls.png",
    )


if __name__ == "__main__":
    main()
