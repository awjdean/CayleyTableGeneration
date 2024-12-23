import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


from ActionFunctionsAlgo.generation.af_cayley_generator import AFCayleyGenerator
from ActionFunctionsAlgo.generation.af_equiv_classes_generator import (
    AFEquivClassGenerator,
)
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls

# Create a simple gridworld with walls
world = Gridworld2DWalls(
    grid_shape=(2, 2),
    wall_positions=[(0.5, 0)],  # Wall between (0,0) and (1,0)
    wall_strategy="identity",
)
world.generate_min_action_transformation_matrix()
equiv_classes_generator = AFEquivClassGenerator(world)
equiv_classes_generator.generate()

actions_cayley_table_generator = AFCayleyGenerator()
actions_cayley_table_generator.generate(equiv_classes_generator)
actions_cayley_table = actions_cayley_table_generator.get_actions_cayley_table()
print(actions_cayley_table)
