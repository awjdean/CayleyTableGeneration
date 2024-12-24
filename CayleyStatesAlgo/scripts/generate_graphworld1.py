import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import AlgebraGenerationMethod
from worlds.graphworlds.graphworld1 import GraphWorld1

# Create and initialize the world
world = GraphWorld1()
world.generate_min_action_transformation_matrix()

# Create and generate the algebra
algebra = TransformationAlgebra(name="graphworld1")
algebra.generate(
    world=world,
    initial_state=(1,),
    method=AlgebraGenerationMethod.STATES_CAYLEY,
)

# Check and display properties
algebra.check_properties()
algebra.print_properties(False)
