import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.transformation_algebra import TransformationAlgebra


def main():
    # Create a new transformation algebra instance with the same name
    algebra = TransformationAlgebra(name="gridworld_2x2_wall")

    # Load the saved data
    print("Loading algebra...")
    algebra.load()  # Will load from ./saved/algebra/gridworld_2x2_wall.pkl

    # Print the loaded tables
    print("\nLoaded tables:")
    print(algebra.cayley_table_states)
    print(algebra.cayley_table_actions)

    # Print the loaded parameters
    print("\nAlgebra generation parameters:")
    print(f"Initial state: {algebra._algebra_generation_parameters['initial_state']}")
    print(f"World config: {algebra._algebra_generation_parameters['world']}")

    algebra.check_properties()

    pass


if __name__ == "__main__":
    main()
