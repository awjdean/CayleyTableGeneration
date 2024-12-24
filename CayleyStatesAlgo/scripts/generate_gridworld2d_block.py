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
from worlds.gridworlds2d.gridworld2d_block import Gridworld2DBlock
from worlds.utils.create_initial_state import create_initial_state_gridworld2d_block

# Define initial positions
initial_agent_position = (0, 0)
initial_block_position = (1, 0)

# Create and initialize the world
world = Gridworld2DBlock(
    grid_shape=(2, 2),
)
world.generate_min_action_transformation_matrix()

# Create and generate the algebra
algebra = TransformationAlgebra(name="gridworld2D_block")
algebra.generate(
    world=world,
    initial_state=create_initial_state_gridworld2d_block(
        initial_agent_position, initial_block_position
    ),
    method=AlgebraGenerationMethod.STATES_CAYLEY,
)

# Check and display properties
algebra.check_properties()
algebra.print_properties(False)
