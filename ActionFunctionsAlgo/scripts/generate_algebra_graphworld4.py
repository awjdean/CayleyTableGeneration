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
from worlds.graphworlds.graphworld4 import GraphWorld4

# Create GraphWorld2 instance
world = GraphWorld4()
world.generate_min_action_transformation_matrix()

# Create and generate global transformation algebra
global_algebra = TransformationAlgebra("graphworld4_global")
global_algebra.generate(world, method=AlgebraGenerationMethod.ACTION_FUNCTION)
global_algebra.check_properties()
global_algebra.print_properties()
# global_algebra.save(None)

print("\n" + "=" * 80 + "\n")

# Create and generate local transformation algebra starting from state (1,)
local_algebra = TransformationAlgebra("graphworld4_local")
local_algebra.generate(
    world, initial_state=(0,), method=AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION
)
local_algebra.check_properties()
local_algebra.print_properties(False)
# local_algebra.save(None)
# print(local_algebra.cayley_table_actions.data)
