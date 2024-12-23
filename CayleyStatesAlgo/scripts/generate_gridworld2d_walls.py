import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import AlgebraGenerationMethod
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls

world = Gridworld2DWalls(
    grid_shape=(2, 2),
    wall_positions=[(0.5, 0)],
    wall_strategy="masked",
)
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2D_walls")
algebra.generate(
    world=world, initial_state=(0, 0), method=AlgebraGenerationMethod.STATES_CAYLEY
)
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
print(algebra.cayley_table_actions)
