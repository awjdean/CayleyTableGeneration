from utils.type_definitions import ActionType, GridPosition2DType, StateType
from worlds.base_world import BaseWorld
from worlds.gridworlds2d.utils.generate_2d_grid_positions import (
    generate_2d_grid_positions,
)
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid


class Gridworld2DBlock(BaseWorld):
    def __init__(self, grid_shape: GridPosition2DType) -> None:
        """
        World states are of the form (agent_x, agent_y, (block_x, block_y)).
        """
        min_actions = ["1", "W", "E", "N", "S"]
        super().__init__(min_actions)
        self._GRID_SHAPE = grid_shape

    def generate_possible_states(self) -> list[StateType]:
        possible_states = []
        possible_agent_positions = generate_2d_grid_positions(
            grid_size=self._GRID_SHAPE
        )
        possible_block_positions = generate_2d_grid_positions(
            grid_size=self._GRID_SHAPE
        )
        for agent_position in possible_agent_positions:
            for block_position in possible_block_positions:
                if agent_position != block_position:
                    state = (*agent_position, block_position)
                    possible_states.append(state)
        return possible_states

    def get_next_state(self, state: StateType, min_action: ActionType):
        agent_position = state[:2]
        block_position = state[2]
        new_agent_position = MoveObject2DGrid(min_action).apply(
            object_position=agent_position, grid_shape=self._GRID_SHAPE
        )
        if new_agent_position == block_position:
            new_block_position = MoveObject2DGrid(min_action).apply(
                object_position=block_position, grid_shape=self._GRID_SHAPE
            )
        else:
            new_block_position = block_position

        next_state = (*new_agent_position, new_block_position)
        return next_state

    def draw(self):
        pass

    def _get_additional_properties_for_save(self) -> dict:
        """Get additional properties specific to Gridworld2DBlock.

        Returns:
            dict: Additional properties including grid shape.
        """
        return {"grid_shape": self._GRID_SHAPE}
