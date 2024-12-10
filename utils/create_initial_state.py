from utils.type_definitions import GridPosition2DType


def create_initial_state_gridworld2d_block(
    agent_position: GridPosition2DType, block_position: GridPosition2DType
):
    return (*agent_position, block_position)


def create_initial_state_gridworld2d_consumables(
    agent_position: GridPosition2DType, consumable_positions: list[GridPosition2DType]
):
    return (*agent_position, (*consumable_positions,))
