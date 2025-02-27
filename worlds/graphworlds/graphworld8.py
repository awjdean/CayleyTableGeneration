"""
This is the group S3, which is also the dihedral group of the trinagle.
"""

from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


class GraphWorld8(BaseWorld):
    def __init__(self) -> None:
        min_actions = ["1", "a", "b"]
        super().__init__(min_actions)

    def generate_possible_states(self) -> list[StateType]:
        return [(1,), (2,), (3,), (4,), (5,), (6,)]

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        min_action_transitions = {
            "1": {
                (1,): (1,),
                (2,): (2,),
                (3,): (3,),
                (4,): (4,),
                (5,): (5,),
                (6,): (6,),
            },
            "a": {
                (1,): (2,),
                (2,): (3,),
                (3,): (1,),
                (4,): (5,),
                (5,): (6,),
                (6,): (4,),
            },
            "b": {
                (1,): (5,),
                (2,): (4,),
                (3,): (6,),
                (4,): (2,),
                (5,): (1,),
                (6,): (3,),
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
