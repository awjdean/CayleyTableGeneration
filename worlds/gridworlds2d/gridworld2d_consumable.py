import itertools

from utils.type_definitions import ActionType, GridPosition2DType, StateType
from worlds.base_world import BaseWorld
from worlds.gridworlds2d.utils.generate_2d_grid_positions import (
    generate_2d_grid_positions,
)
from worlds.gridworlds2d.utils.move_objects_2d import MoveObject2DGrid
from worlds.utils.undefined_action_strat import UndefinedActionStrat


class Gridworld2DConsumable(BaseWorld):
    def __init__(
        self,
        grid_shape: GridPosition2DType,
        consumable_positions: list[GridPosition2DType],
        consume_strategy: str,
    ):
        """
        Initializes the Gridworld2DConsumable instance.
        States are of the form:
        (agent_x, agent_y, ((consumable1_x, consumable1_y),
          (consumable2_x, consumable2_y),
          ...))

        Args:
            grid_shape (GridPosition2DType): The shape of the grid.
            consumable_positions (list[GridPosition2DType]): A list of positions where
             consumables are located.
            consume_strategy (str): The strategy for consuming items, must be either
             'identity' or 'masked'.

        Raises:
            ValueError: If consume_strategy is not 'identity' or 'masked'.
        """
        min_actions = ["1", "W", "E", "N", "S", "C"]
        super().__init__(min_actions)
        if consume_strategy not in ["identity", "masked"]:
            raise ValueError("wall_strategy must be either 'identity' or 'masked'")
        self._CONSUME_STRATEGY = consume_strategy
        self._GRID_SHAPE = grid_shape
        self._CONSUMABLE_POSITIONS = consumable_positions

    def generate_possible_states(self) -> list[StateType]:
        """
        Generates all possible states of the grid based on agent and consumable
         positions.

        Returns:
            list[StateType]: A list of possible states represented as tuples.
        """
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
        """
        Computes the next state based on the current state and the action taken.

        Args:
            state (StateType): The current state of the grid.
            min_action (ActionType): The action to be performed.

        Returns:
            StateType: The next state after the action is applied.
        """
        if min_action == "C":
            next_state = _apply_consume_action(state, self._CONSUME_STRATEGY)
        else:
            agent_position = state[:2]
            consumable_positions = state[2]
            new_agent_position = MoveObject2DGrid(min_action).apply(
                object_position=agent_position, grid_shape=self._GRID_SHAPE
            )
            next_state = (*new_agent_position, consumable_positions)

        return next_state

    def draw(self):
        """
        Draws the current state of the grid. (To be implemented)
        """
        # TODO: Implement this.
        pass

    def _get_additional_properties_for_save(self) -> dict:
        """Get additional properties specific to Gridworld2DConsumable.

        Returns:
            dict: Additional properties including grid shape, consumable positions,
                 and consume strategy.
        """
        return {
            "grid_shape": self._GRID_SHAPE,
            "consumable_positions": self._CONSUMABLE_POSITIONS,
            "consume_strategy": self._CONSUME_STRATEGY,
        }


def _apply_consume_action(state: StateType, consume_strategy: str) -> StateType:
    """
    Applies the consume action to the current state based on the consume strategy.

    Args:
        state (StateType): The current state of the grid.
        consume_strategy (str): The strategy for consuming items.

    Returns:
        StateType: The new state after the consume action is applied.
    """
    agent_position = state[:2]
    consumable_positions = state[2]
    if agent_position in consumable_positions:
        new_consumable_positions = _remove_first_consumable(
            consumable_positions=consumable_positions, agent_position=agent_position
        )
        new_state = (*agent_position, new_consumable_positions)
    else:
        new_state = UndefinedActionStrat(consume_strategy).apply(state)
    return new_state


def _remove_first_consumable(
    consumable_positions: tuple[GridPosition2DType, ...],
    agent_position: GridPosition2DType,
) -> tuple[GridPosition2DType, ...]:
    """
    Removes the first consumable from the list of consumable positions based on the
    agent's position.

    Args:
        consumable_positions (tuple[GridPosition2DType, ...]): The current positions of
          consumables.
        agent_position (GridPosition2DType): The position of the agent.

    Returns:
        tuple[GridPosition2DType, ...]: The new tuple of consumable positions after
         removal.
    """
    consumable_positions_list = list(consumable_positions)
    idx = consumable_positions_list.index(agent_position)
    consumable_positions_list.pop(idx)
    new_consumable_positions = tuple(consumable_positions_list)
    return new_consumable_positions
