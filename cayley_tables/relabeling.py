from cayley_tables.cayley_table_states import CayleyTableStates
from cayley_tables.equiv_classes import EquivClasses
from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


def relabel_equiv_classes(
    equiv_classes: EquivClasses,
    cayley_table_states: CayleyTableStates,
    initial_state: StateType,
    world: BaseWorld,
) -> tuple[EquivClasses, CayleyTableStates]:
    """Relabel equivalence classes using shortest action sequences.

    Creates new equivalence classes where each class is labeled by its shortest
    action sequence (breaking ties alphabetically).

    Args:
        equiv_classes: Original equivalence classes
        cayley_table_states: Original Cayley table for states
        initial_state: Initial state of the world
        world: World instance for validation

    Returns:
        Tuple containing:
        - New equivalence classes with updated labels
        - New Cayley table for states with updated labels

    Note:
        The relabeling preserves all relationships and only changes the labels
        used to identify each equivalence class.
    """
    # Create new instances
    new_equiv_classes = EquivClasses()
    label_changes: dict[ActionType, ActionType] = {}

    # Relabel each equivalence class
    for old_label in equiv_classes.get_labels():
        elements = equiv_classes.get_class_elements(old_label)
        # Sort by length first, then alphabetically
        sorted_elements = sorted(list(elements))
        sorted_elements = sorted(sorted_elements, key=len)
        new_label = sorted_elements[0]

        # Create new class with same elements but new label
        new_equiv_classes.create_new_class(
            class_label=new_label,
            outcome=equiv_classes.get_class_outcome(old_label),
            elements=sorted_elements,
        )
        label_changes[old_label] = new_label

    # Update Cayley table with new labels
    new_cayley_table_states = CayleyTableStates()
    for old_row in equiv_classes.get_labels():
        new_row = label_changes[old_row]
        new_cayley_table_states.data[new_row] = {}
        for old_col in equiv_classes.get_labels():
            outcome = cayley_table_states.data[old_row][old_col]
            new_col = label_changes[old_col]
            new_cayley_table_states.data[new_row][new_col] = outcome

    return new_equiv_classes, new_cayley_table_states
