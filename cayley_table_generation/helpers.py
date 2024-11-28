from type_definitions import CayleyTableStatesType, StateType
from worlds.base_world import BaseWorld


def add_outcome_to_cayley_table(
    cayley_table: CayleyTableStatesType,
    row_label: str,
    column_label: str,
    outcome: StateType,
):
    """
    Adds an outcome to the specified row and column of the Cayley table.
    Row-column pair must exist.

    Raises:
        KeyError: If the row or column does not exist in the Cayley table.
    """
    if row_label not in cayley_table:
        raise KeyError(f"Row '{row_label}' does not exist in the Cayley table.")

    if column_label not in cayley_table[row_label]:
        raise KeyError(
            f"Column '{column_label}' does not exist in the "
            f"Cayley table for row '{row_label}'."
        )

    cayley_table[row_label][column_label] = outcome


def generate_action_sequence_outcome(
    action_sequence, initial_state, world: BaseWorld
) -> StateType:
    """
    Generates outcome of applying an action sequence to the world from the
      initial_state.
    """
    world.set_state(initial_state)
    world.apply_action_sequence(action_sequence)
    return world.get_state()
