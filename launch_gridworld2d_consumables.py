from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import GridPosition2DType
from worlds.gridworlds2d.gridworld2d_consumable import Gridworld2DConsumable

consumable_positions = [(0, 0), (1, 0)]
initial_agent_position = (0, 0)


def get_initial_state(
    agent_position: GridPosition2DType, consumable_positions: list[GridPosition2DType]
):
    return (*agent_position, (*consumable_positions,))


world = Gridworld2DConsumable(
    grid_shape=(2, 3),
    consumable_positions=consumable_positions,
    consume_strategy="identity",
)
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="gridworld2DConsumable")
algebra.generate_cayley_table_states(
    world=world,
    initial_state=get_initial_state(
        agent_position=initial_agent_position, consumable_positions=consumable_positions
    ),
)
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra.generate_cayley_table_actions()
print(algebra.cayley_table_actions)
