import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.find_isomorphism import check_isomorphism
from transformation_algebra.transformation_algebra import TransformationAlgebra


def main():
    # Load the first algebra
    algebra1 = TransformationAlgebra(name="gridworld_2x2_wall")
    print(f"Loading algebra1 from: ./saved/algebra/{algebra1.name}.pkl")
    algebra1.load()

    # Load the second algebra
    algebra2 = TransformationAlgebra(name="gridworld_2x2_wall_2")
    print(f"Loading algebra2 from: ./saved/algebra/{algebra2.name}.pkl")
    algebra2.load()

    # Check for isomorphism
    print("\nChecking for isomorphism...")
    result = check_isomorphism(algebra1, algebra2)

    # Print results
    print("\nResults:")
    print(f"Isomorphic: {result['is_isomorphic']}")
    if not result["is_isomorphic"]:
        print(f"Reason: {result['reason']}")
    else:
        print("\nIsomorphism mapping:")
        print(result["mapping_str"])


if __name__ == "__main__":
    main()
