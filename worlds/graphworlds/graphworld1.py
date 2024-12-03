from type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


class GraphWorld1(BaseWorld):
    def __init__(self) -> None:
        super().__init__()

    def get_possible_states(self) -> list[StateType]:
        return [(1,), (2,), (3,)]

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        transitions = {
            "1": {(1,): (1,), (2,): (2,), (3,): (3,)},
            "a": {(1,): (2,), (2,): (3,), (3,): (1,)},
            "b": {(1,): (2,), (2,): (1,), (3,): (3,)},
        }

        if min_action in transitions:
            next_state = transitions[min_action].get(state)
            if next_state is None:
                raise ValueError(
                    f"Invalid state: '{state}' for action: '{min_action}'."
                )
            return next_state
        else:
            raise ValueError(f"Invalid action: '{min_action}'.")
