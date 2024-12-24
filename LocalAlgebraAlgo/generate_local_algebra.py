import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.transformation_algebra import TransformationAlgebra
from transformation_algebra.utils.algebra_generation_methods import (
    AlgebraGenerationMethod,
)
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls

# Create a simple gridworld with walls
world = Gridworld2DWalls(
    grid_shape=(2, 2),
    wall_positions=[],  # Wall between (0,0) and (1,0)
    wall_strategy="identity",
)
world.generate_min_action_transformation_matrix()

# Choose an initial state to analyze from
initial_state = (0, 0)  # Starting at the bottom-left corner

# Create transformation algebra instance
algebra = TransformationAlgebra("gridworld_2x2_wall")

# Generate the algebra using local action function method
algebra.generate(
    world=world,
    initial_state=initial_state,
    method=AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION,
)

algebra.check_properties()
algebra.print_properties(False)
