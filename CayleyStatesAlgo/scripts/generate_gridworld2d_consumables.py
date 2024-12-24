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
from worlds.gridworlds2d.gridworld2d_consumable import Gridworld2DConsumable
from worlds.utils.create_initial_state import (
    create_initial_state_gridworld2d_consumables,
)

# Define initial positions
consumable_positions = [(0, 0)]
initial_agent_position = (0, 0)

# Create and initialize the world
world = Gridworld2DConsumable(
    grid_shape=(2, 2),
    consumable_positions=consumable_positions,
    consume_strategy="masked",
)
world.generate_min_action_transformation_matrix()

# Create and generate the algebra
algebra = TransformationAlgebra(name="gridworld2DConsumable")
algebra.generate(
    world=world,
    initial_state=create_initial_state_gridworld2d_consumables(
        agent_position=initial_agent_position, consumable_positions=consumable_positions
    ),
    method=AlgebraGenerationMethod.STATES_CAYLEY,
)

# Check and display properties
algebra.check_properties()
algebra.print_properties(False)
