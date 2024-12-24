import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import AlgebraGenerationMethod
from worlds.gridworlds2d.gridworld2d import Gridworld2D

# Create and initialize the world
world = Gridworld2D(
    grid_shape=(2, 2),
)
world.generate_min_action_transformation_matrix()

# Create and generate the algebra
algebra = TransformationAlgebra(name="gridworld2D")
algebra.generate(
    world=world,
    initial_state=(0, 0),
    method=AlgebraGenerationMethod.STATES_CAYLEY,
)

# Check and display properties
algebra.check_properties()
algebra.print_properties(False)
