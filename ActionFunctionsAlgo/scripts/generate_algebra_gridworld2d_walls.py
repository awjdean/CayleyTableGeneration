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

# Define wall positions and grid shape
grid_shape = (2, 2)
# wall_positions = []  # Wall between (0,0) and (1,0)
wall_positions = [(0.5, 1.0)]  # Wall between (0,1) and (1,1)
wall_strategy = "identity"  # or "masked"

# Create Gridworld2DWalls instance
world = Gridworld2DWalls(
    grid_shape=grid_shape, wall_positions=wall_positions, wall_strategy=wall_strategy
)
world.generate_min_action_transformation_matrix()

# Create and generate global transformation algebra
# global_algebra = TransformationAlgebra("gridworld2d_walls_global")
# global_algebra.generate(world, method=AlgebraGenerationMethod.ACTION_FUNCTION)
# global_algebra.check_properties()
# global_algebra.print_properties()
# global_algebra.save(None)

print("\n" + "=" * 80 + "\n")

initial_state = (1, 0)
local_algebra = TransformationAlgebra("test")
local_algebra.generate(
    world,
    initial_state=initial_state,
    method=AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION,
)
local_algebra.check_properties()
local_algebra.print_properties()
local_algebra.save(None)
