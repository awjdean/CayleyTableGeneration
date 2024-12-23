from CayleyStatesAlgo.generation.cayley_table_states import CayleyTableStates
from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.cayley_table_actions import CayleyTableActions
from utils.equiv_classes import EquivClasses
from utils.type_definitions import ActionType


def get_label_changes(equiv_classes: EquivClasses) -> dict[ActionType, ActionType]:
    """
    Create a mapping from old labels to new labels based on shortest action sequences.

    Args:
        equiv_classes: Original equivalence classes

    Returns:
        Dictionary mapping old labels to new labels
    """
    label_changes: dict[ActionType, ActionType] = {}

    # Create mapping for each equivalence class
    for old_label in equiv_classes.get_labels():
        elements = equiv_classes.get_class_elements(old_label)
        # Sort by length first, then alphabetically
        sorted_elements = sorted(list(elements))
        sorted_elements = sorted(sorted_elements, key=len)
        new_label = sorted_elements[0]
        label_changes[old_label] = new_label

    return label_changes


def relabel_equiv_classes(
    equiv_classes: EquivClasses,
    label_changes: dict[ActionType, ActionType],
) -> EquivClasses:
    """
    Create new equivalence classes with updated labels.

    Args:
        equiv_classes: Original equivalence classes
        label_changes: Dictionary mapping old labels to new labels

    Returns:
        New equivalence classes with updated labels
    """
    new_equiv_classes = EquivClasses()

    # Create new classes with updated labels
    for old_label in equiv_classes.get_labels():
        new_label = label_changes[old_label]
        elements = equiv_classes.get_class_elements(old_label)
        # Sort elements for consistency
        sorted_elements = sorted(list(elements))

        new_equiv_classes.create_new_class(
            class_label=new_label,
            outcome=equiv_classes.get_class_outcome(old_label),
            elements=sorted_elements,
        )

    return new_equiv_classes


def relabel_states_cayley_table(
    cayley_table: CayleyTableStates,
    label_changes: dict[ActionType, ActionType],
) -> CayleyTableStates:
    """
    Create new Cayley table with updated labels.

    Args:
        cayley_table: Original Cayley table
        label_changes: Dictionary mapping old labels to new labels

    Returns:
        New Cayley table with updated labels
    """
    new_cayley_table = CayleyTableStates()

    # Update table entries with new labels
    for old_row in cayley_table.get_row_labels():
        new_row = label_changes[old_row]
        new_cayley_table.data[new_row] = {}
        for old_col in cayley_table.get_row_labels():
            new_col = label_changes[old_col]
            new_cayley_table.data[new_row][new_col] = cayley_table.data[old_row][
                old_col
            ]

    return new_cayley_table


def relabel_actions_cayley_table(
    cayley_table: CayleyTableActions,
    label_changes: dict[ActionType, ActionType],
) -> CayleyTableActions:
    """
    Create new actions Cayley table with updated labels.

    Args:
        cayley_table: Original actions Cayley table
        label_changes: Dictionary mapping old labels to new labels

    Returns:
        New actions Cayley table with updated labels
    """
    new_cayley_table = CayleyTableActions()

    # Update table entries with new labels
    for old_row in cayley_table.get_all_actions():
        new_row = label_changes[old_row]
        new_cayley_table.data[new_row] = {}
        for old_col in cayley_table.get_all_actions():
            new_col = label_changes[old_col]
            # The value in the actions table is also an action that needs relabeling
            old_table_entry = cayley_table.data[old_row][old_col]
            new_table_entry = label_changes[old_table_entry]
            new_cayley_table.data[new_row][new_col] = new_table_entry

    return new_cayley_table


def relabel_algebra_components(
    algebra: TransformationAlgebra,
) -> TransformationAlgebra:
    """
    Create a new TransformationAlgebra with all components relabeled using shortest
      action sequences (breaking ties alphabetically).

    Args:
        algebra: Original TransformationAlgebra instance

    Returns:
        New TransformationAlgebra with relabeled components

    Note:
        The relabeling preserves all relationships and only changes the labels
        used to identify each equivalence class.
    """
    # Get mapping from old to new labels
    label_changes = get_label_changes(algebra.equiv_classes)

    # Create new algebra instance
    relabeled_algebra = TransformationAlgebra(name=f"{algebra.name}_relabeled")

    # Copy generation parameters
    relabeled_algebra._algebra_generation_parameters = (
        algebra._algebra_generation_parameters
    )

    # Create new components with updated labels
    relabeled_algebra.equiv_classes = relabel_equiv_classes(
        algebra.equiv_classes, label_changes
    )
    relabeled_algebra.cayley_table_states = relabel_states_cayley_table(
        algebra.cayley_table_states, label_changes
    )
    relabeled_algebra.cayley_table_actions = relabel_actions_cayley_table(
        algebra.cayley_table_actions, label_changes
    )

    return relabeled_algebra
