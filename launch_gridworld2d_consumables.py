from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.create_initial_state import create_initial_state_gridworld2d_consumables
from worlds.gridworlds2d.gridworld2d_consumable import Gridworld2DConsumable

consumable_positions = [(0, 0)]
initial_agent_position = (0, 0)


world = Gridworld2DConsumable(
    grid_shape=(2, 2),
    consumable_positions=consumable_positions,
    consume_strategy="masked",
)
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2DConsumable")
algebra.generate(
    world=world,
    initial_state=create_initial_state_gridworld2d_consumables(
        agent_position=initial_agent_position, consumable_positions=consumable_positions
    ),
)
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra._generate_cayley_table_actions()
print(algebra.cayley_table_actions)
