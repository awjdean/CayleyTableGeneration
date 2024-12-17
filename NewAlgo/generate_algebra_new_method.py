import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from NewAlgo.new_actions_cayley_generator import NewActionsCayleyGenerator
from NewAlgo.new_equiv_classes_generator import NewEquivClassGenerator
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls

# Create a simple gridworld with walls
world = Gridworld2DWalls(
    grid_shape=(3, 3),
    wall_positions=[(0.5, 0), (0, 0.5)],  # Wall between (0,0) and (1,0)
    wall_strategy="masked",
)
world.generate_min_action_transformation_matrix()
equiv_classes = NewEquivClassGenerator(world)
equiv_classes.generate()

actions_cayley_table_generator = NewActionsCayleyGenerator()
actions_cayley_table_generator.generate(equiv_classes)
actions_cayley_table = actions_cayley_table_generator.get_actions_cayley_table()
print(actions_cayley_table)
