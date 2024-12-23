from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


class GraphWorld2(BaseWorld):
    def __init__(self) -> None:
        min_actions = ["1", "a", "b"]
        super().__init__(min_actions)

    def generate_possible_states(self) -> list[StateType]:
        return [(1,), (2,), (3,)]

    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        min_action_transitions = {
            "1": {(1,): (1,), (2,): (2,), (3,): (3,)},
            "a": {(1,): (3,), (2,): (2,), (3,): (1,)},
            "b": {(1,): (2,), (2,): (1,), (3,): (1,)},
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
