import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


from transformation_algebra.transformation_algebra import TransformationAlgebra
from worlds.gridworlds2d.gridworld2d import Gridworld2D

world = Gridworld2D(
    grid_shape=(2, 2),
)
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2D")
algebra.generate(world=world, initial_state=(0, 0))
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra._generate_cayley_table_actions()
print(algebra.cayley_table_actions)
