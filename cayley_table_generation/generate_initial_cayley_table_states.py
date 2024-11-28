from cayley_table_generation.helpers import generate_action_sequence_outcome
from type_definitions import CayleyTableStatesType, StateType
from worlds.base_world import BaseWorld


def generate_initial_cayley_table_states(
    equiv_class_labels: list[str],
    initial_state: StateType,
    world: BaseWorld,
) -> CayleyTableStatesType:
    """
    Generate initial state Cayley table.
    """
    cayley_table_states = {}
    for row_label in equiv_class_labels:
        cayley_table_states[row_label] = {}
        for column_label in equiv_class_labels:
            action_sequence = column_label + row_label
            outcome = generate_action_sequence_outcome(
                action_sequence=action_sequence,
                initial_state=initial_state,
                world=world,
            )
            cayley_table_states[row_label][column_label] = outcome
    return cayley_table_states


__all__ = ["generate_initial_cayley_table_states"]
