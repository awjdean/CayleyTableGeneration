""" """

from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


class GraphWorld7_w_minus_1(BaseWorld):
    def __init__(self) -> None:
        min_actions = ["1", "a", "b", "c"]
        super().__init__(min_actions)

    def generate_possible_states(self) -> list[StateType]:
        return [(-2,), (-1,), (0,), (1,), (2,), (3,), (4,)]

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        min_action_transitions = {
            "1": {
                (-2,): (-2,),
                (-1,): (-1,),
                (0,): (0,),
                (1,): (1,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
            },
            "a": {
                (-2,): (0,),
                (-1,): (0,),
                (0,): (1,),
                (1,): (1,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
            },
            "b": {
                (-2,): (-1,),
                (-1,): (-2,),
                (0,): (2,),
                (1,): (4,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
            },
            "c": {
                (-2,): (-2,),
                (-1,): (-1,),
                (0,): (3,),
                (1,): (4,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
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


class GraphWorld7_w2(BaseWorld):
    def __init__(self) -> None:
        min_actions = ["1", "a", "b", "c"]
        super().__init__(min_actions)

    def generate_possible_states(self) -> list[StateType]:
        return [(1,), (2,), (3,), (4,)]

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        min_action_transitions = {
            "1": {(1,): (1,), (2,): (2,), (3,): (3,), (4,): (4,)},
            "a": {
                (1,): (1,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
            },
            "b": {
                (1,): (4,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
            },
            "c": {
                (1,): (4,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
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
