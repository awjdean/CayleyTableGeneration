from cayley_tables.cayley_table_states import CayleyTableStates
from cayley_tables.states_cayley_table_generation.action_outcome import (
    generate_action_outcome,
)
from utils.type_definitions import StateType
from worlds.base_world import BaseWorld


def generate_initial_cayley_table_states(
    equiv_class_labels: list[str],
    initial_state: StateType,
    world: BaseWorld,
) -> CayleyTableStates:
    """
    Generate initial state Cayley table.
    """
    cayley_table_states = CayleyTableStates()
    for row_label in equiv_class_labels:
        cayley_table_states.data[row_label] = {}
        for column_label in equiv_class_labels:
            action_sequence = column_label + row_label
            outcome = generate_action_outcome(
                action=action_sequence,
                initial_state=initial_state,
                world=world,
            )
            cayley_table_states.data[row_label][column_label] = outcome
    return cayley_table_states


__all__ = ["generate_initial_cayley_table_states"]