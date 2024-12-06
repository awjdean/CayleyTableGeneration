from transformation_algebra.transformation_algebra import TransformationAlgebra
from worlds.gridworlds2d.gridworld2d_consumable import Gridworld2DConsumable

world = Gridworld2DConsumable(
    grid_shape=(2, 3),
    consumable_positions=[(0, 0), (1, 0)],
)
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2D")
algebra.generate_cayley_table_states(world=world, initial_state=(0, 0))
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra.generate_cayley_table_actions()
print(algebra.cayley_table_actions)
