import itertools

from utils.type_definitions import ActionType, GridPosition2DType, StateType
from worlds.base_world import BaseWorld
from worlds.gridworlds2d.utils.generate_states import generate_states


class Gridworld2DConsumable(BaseWorld):
    def __init__(
        self,
        grid_shape: GridPosition2DType,
        consumable_positions: list[GridPosition2DType],
    ):
        """
        States are of the form: (agent_x, agent_y, (consumable1_x, consumable1_y), ...)
        """
        super().__init__()
        self._GRID_SHAPE = grid_shape
        self._CONSUMABLE_POSITIONS = consumable_positions

        pass

    def get_possible_states(self) -> list[StateType]:
        possible_states = []
        agent_positions = generate_states(grid_size=self._GRID_SHAPE)
        for agent_position in agent_positions:
            for num_consumables in range(len(self._CONSUMABLE_POSITIONS) + 1):
                for consumable_positions in itertools.combinations(
                    self._CONSUMABLE_POSITIONS, num_consumables
                ):
                    state = (*agent_position, *consumable_positions)
                    possible_states.append(state)
        return possible_states

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        pass

    def draw(self):
        pass
