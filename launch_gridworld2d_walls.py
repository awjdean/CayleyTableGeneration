from transformation_algebra.transformation_algebra import TransformationAlgebra
from worlds.gridworlds2d.gridworld2d_walls import Gridworld2DWalls

world = Gridworld2DWalls(
    grid_shape=(2, 3),
    wall_positions=[(0.5, 0)],
    wall_strategy="masked",
)
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2D_walls")
algebra.generate_cayley_table_states(world=world, initial_state=(0, 0))
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra.generate_cayley_table_actions()
print(algebra.cayley_table_actions)