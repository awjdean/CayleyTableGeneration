from type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


def generate_action_outcome(
    action: ActionType, initial_state: StateType, world: BaseWorld
) -> StateType:
    """
    Generates outcome of applying an action sequence to the world from the
      initial_state.
    action * w_{0}.
    """
    world.set_state(initial_state)
    world.apply_action_sequence(action)
    return world.get_state()
