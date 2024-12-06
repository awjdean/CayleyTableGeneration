from utils.type_definitions import GridPosition2DType
from worlds.base_world import BaseWorld
from worlds.gridworlds2d.utils.generate_2d_grid_positions import (
    generate_2d_grid_positions,
)
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid


class Gridworld2DBlock(BaseWorld):
    def __init__(
        self, grid_size: GridPosition2DType, block_position: GridPosition2DType
    ) -> None:
        """
        World states are of the form (agent_x, agent_y, (block_x, block_y)).
        """
        super().__init__()
        self._GRID_SIZE = grid_size
        self._BLOCK_POSITION = block_position

    def get_possible_states(self) -> list[GridPosition2DType]:
        # TODO: Check this.
        possible_states = []
        possible_agent_positions = generate_2d_grid_positions(grid_size=self._GRID_SIZE)
        possible_block_positions = generate_2d_grid_positions(grid_size=self._GRID_SIZE)
        for agent_position in possible_agent_positions:
            for block_position in possible_block_positions:
                if agent_position != block_position:
                    state = (*agent_position, block_position)
                    possible_states.append(state)
        return possible_states

    # TODO: Check this.
    def get_next_state(self, state, min_action):
        agent_position = state[:2]
        block_position = state[2]
        new_agent_position = MoveObject2DGrid(min_action).apply(
            object_position=agent_position, grid_shape=self._GRID_SIZE
        )
        if new_agent_position == block_position:
            new_block_position = MoveObject2DGrid(min_action).apply(
                object_position=block_position, grid_shape=self._GRID_SIZE
            )
        else:
            new_block_position = block_position

        next_state = (*new_agent_position, new_block_position)
        return next_state

    def draw(self):
        pass
