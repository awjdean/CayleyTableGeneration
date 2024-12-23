import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import AlgebraGenerationMethod
from worlds.graphworlds.graphworld2_local_not_global_group import GraphWorld2

# Create GraphWorld2 instance
world = GraphWorld2()
world.generate_min_action_transformation_matrix()

# Create and generate global transformation algebra
global_algebra = TransformationAlgebra("graphworld2_global")
global_algebra.generate(world, method=AlgebraGenerationMethod.ACTION_FUNCTION)
global_algebra.check_properties()
global_algebra.print_properties()
global_algebra.save(None)

print("\n" + "=" * 80 + "\n")

# Create and generate local transformation algebra starting from state (1,)
local_algebra = TransformationAlgebra("graphworld2_local")
local_algebra.generate(
    world, initial_state=(1,), method=AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION
)
local_algebra.check_properties()
local_algebra.print_properties(True)
local_algebra.save(None)
