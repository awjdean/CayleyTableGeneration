""" """

from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld
from worlds.utils.undefined_state import UndefinedStates


class GraphWorld5(BaseWorld):
    def __init__(self) -> None:
        min_actions = ["1", "a", "b", "c", "d", "e"]
        super().__init__(min_actions)

    def generate_possible_states(self) -> list[StateType]:
        return [(0,), (1,), (2,), (3,)]

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        min_action_transitions = {
            "1": {(0,): (0,), (1,): (1,), (2,): (2,), (3,): (3,)},
            "a": {
                (0,): UndefinedStates.BASIC.value,
                (1,): (2,),
                (2,): UndefinedStates.BASIC.value,
                (3,): UndefinedStates.BASIC.value,
            },
            "b": {
                (0,): UndefinedStates.BASIC.value,
                (1,): (2,),
                (2,): UndefinedStates.BASIC.value,
                (3,): UndefinedStates.BASIC.value,
            },
            "c": {
                (0,): (1,),
                (1,): UndefinedStates.BASIC.value,
                (2,): UndefinedStates.BASIC.value,
                (3,): UndefinedStates.BASIC.value,
            },
            "d": {
                (0,): UndefinedStates.BASIC.value,
                (1,): UndefinedStates.BASIC.value,
                (2,): (0,),
                (3,): UndefinedStates.BASIC.value,
            },
            "e": {
                (0,): UndefinedStates.BASIC.value,
                (1,): UndefinedStates.BASIC.value,
                (2,): (3,),
                (3,): UndefinedStates.BASIC.value,
            },
        }

        if min_action in min_action_transitions:
            next_state = min_action_transitions[min_action].get(state)
            if next_state is None:
                raise ValueError(
                    f"Invalid state: '{state}' for action: '{min_action}'."
                )
            return next_state
        else:
            raise ValueError(f"Invalid action: '{min_action}'.")
