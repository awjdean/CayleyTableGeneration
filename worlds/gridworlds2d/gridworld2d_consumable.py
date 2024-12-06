import itertools

from undefined_action_strat import UndefinedActionStrat
from utils.type_definitions import ActionType, GridPosition2DType, StateType
from worlds.base_world import BaseWorld
from worlds.gridworlds2d.utils.generate_2d_grid_positions import (
    generate_2d_grid_positions,
)
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid


class Gridworld2DConsumable(BaseWorld):
    def __init__(
        self,
        grid_shape: GridPosition2DType,
        consumable_positions: list[GridPosition2DType],
        consume_strategy: str,
    ):
        """
        States are of the form:
        (agent_x, agent_y, ((consumable1_x, consumable1_y),
          (consumable2_x, consumable2_y),
          ...))
        """
        super().__init__()
        if consume_strategy not in ["identity", "masked"]:
            raise ValueError("wall_strategy must be either 'identity' or 'masked'")
        self._CONSUME_STRATEGY = consume_strategy
        self._GRID_SHAPE = grid_shape
        self._CONSUMABLE_POSITIONS = consumable_positions
        self._MIN_ACTIONS = ["1", "W", "E", "N", "S", "C"]

    def get_possible_states(self) -> list[StateType]:
        possible_states = []
        agent_positions = generate_2d_grid_positions(grid_size=self._GRID_SHAPE)
        for agent_position in agent_positions:
            for num_consumables in range(len(self._CONSUMABLE_POSITIONS) + 1):
                for consumable_positions in itertools.combinations(
                    self._CONSUMABLE_POSITIONS, num_consumables
                ):
                    state = (*agent_position, (*consumable_positions,))
                    possible_states.append(state)
        return possible_states

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        if min_action == "C":
            next_state = apply_consume_action(state, self._CONSUME_STRATEGY)
        else:
            agent_position = state[:2]
            consumable_positions = state[2]
            new_agent_position = MoveObject2DGrid(min_action).apply(
                object_position=agent_position, grid_shape=self._GRID_SHAPE
            )
            next_state = (*new_agent_position, consumable_positions)

        return next_state

    def draw(self):
        pass


def apply_consume_action(state: StateType, consume_strategy: str) -> StateType:
    agent_position = state[:2]
    consumable_positions = state[2]
    if agent_position in consumable_positions:
        new_consumable_positions = remove_first_consumable(
            consumable_positions=consumable_positions, agent_position=agent_position
        )
        new_state = (*agent_position, new_consumable_positions)
    else:
        new_state = UndefinedActionStrat(consume_strategy).apply(state)
    return new_state


def remove_first_consumable(
    consumable_positions: tuple, agent_position: GridPosition2DType
):
    consumable_positions_list = list(consumable_positions)
    idx = consumable_positions_list.index(agent_position)
    consumable_positions_list.pop(idx)
    new_consumable_positions = tuple(consumable_positions_list)
    return new_consumable_positions
