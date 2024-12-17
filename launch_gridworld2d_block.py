from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.create_initial_state import create_initial_state_gridworld2d_block
from worlds.gridworlds2d.gridworld2d_block import Gridworld2DBlock

initial_agent_position = (0, 0)
initial_block_position = (1, 0)

world = Gridworld2DBlock(
    grid_shape=(3, 2),
)


world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2D_block")
algebra.generate(
    world=world,
    initial_state=create_initial_state_gridworld2d_block(
        initial_agent_position, initial_block_position
    ),
)
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra._generate_cayley_table_actions()
print(algebra.cayley_table_actions)
