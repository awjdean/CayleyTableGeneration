import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import AlgebraGenerationMethod
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls

# Create a simple gridworld with walls
world = Gridworld2DWalls(
    grid_shape=(2, 2),
    wall_positions=[(0.5, 0)],  # Wall between (0,0) and (1,0)
    wall_strategy="identity",
)
world.generate_min_action_transformation_matrix()

# Create and initialize the transformation algebra
algebra = TransformationAlgebra(name="2x2_gridworld_with_wall")

# Generate the algebra using the action function method
algebra.generate(world=world, method=AlgebraGenerationMethod.ACTION_FUNCTION)

# Check and print the algebraic properties
algebra.check_properties()
algebra.print_properties(details=True)

# Optionally save the algebra
algebra.save(None)  # This will save to ./saved/algebra/2x2_gridworld_with_wall.pkl
