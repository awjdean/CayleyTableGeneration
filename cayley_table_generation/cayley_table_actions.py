import pandas as pd

from cayley_table_generation.cayley_table_states import CayleyTableStates
from cayley_table_generation.equiv_classes import EquivClasses
from type_definitions import ActionType, CayleyTableActionsDataType, StateType
from worlds.base_world import BaseWorld


class CayleyTableActions:
    def __init__(self):
        self.data: CayleyTableActionsDataType = {}

    def __str__(self):
        if not self.data:
            return "cayley_table_actions: CayleyTableActions = {}"
        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")
        # Return the string representation of the DataFrame
        return f"cayley_table_actions =\n{df}"


def generate_cayley_table_actions(equiv_classes: EquivClasses) -> CayleyTableActions:
    # Create cayley_table_actions.
    cayley_table_actions = CayleyTableActions()
    # Initialise rows.
    for row_label in equiv_classes.get_labels():
        cayley_table_actions.data[row_label] = {}

    # Fill cayley_table_actions.
    ## For each entry in cayley_table_actions:
    for row_label in equiv_classes.get_labels():
        for column_label in equiv_classes.get_labels():
            action = column_label + row_label
            class_label = equiv_classes.find_element_class(action)
            if class_label is None:
                raise ValueError(
                    f"Action '{action}' not found in any equivalence class."
                )
            cayley_table_actions.data[row_label][column_label] = class_label

    ## Combine row and column labels: (column_label \circ row_label).
    ## Find (column_label \circ row_label) in equiv_classes.
    ## Fill entry in cayley_table_actions with labelling element for that equiv class.
    ## If no entry, then raise exception, and search for equivalent element in states
    #  Cayley table.

    return cayley_table_actions


# TODO: put into own file.
def relabel_equiv_classes_and_state_cayley_table(
    equiv_classes: EquivClasses,
    cayley_table_states: CayleyTableStates,
    initial_state: StateType,
    world: BaseWorld,
) -> tuple[EquivClasses, CayleyTableStates]:
    """
    Relabel equivalence classes with the shortest minimum action sequence, then
     alphabetically.
    """
    # TODO: Check this function.
    # Create new instances for equiv_classes, cayley_table_states.
    new_equiv_classes: EquivClasses = EquivClasses()
    label_change_dict: dict[ActionType, ActionType] = {}

    # Go through equiv_classes, work out new class_label, then copy over to new
    #  instance.
    for old_class_label in equiv_classes.get_labels():
        # Get elements.
        elements = equiv_classes.get_class_elements(old_class_label)
        # Sort elements by length then alphabetical order.
        sorted_elements = sorted(list(elements))
        sorted_elements = sorted(sorted_elements, key=len)
        # Get new class label.
        new_class_label = sorted_elements[0]
        # Constuct new_equiv_classes.
        new_equiv_classes.create_new_class(
            class_label=new_class_label,
            outcome=equiv_classes.get_class_outcome(old_class_label),
            elements=sorted_elements,
        )
        # Store label change.
        label_change_dict[old_class_label] = new_class_label

    # Construct new_cayley_table_states.
    new_cayley_table_states = CayleyTableStates()
    for old_row_label in equiv_classes.get_labels():
        for old_column_label in equiv_classes.get_labels():
            # Get outcome from old cayley_table_states.
            outcome = cayley_table_states.data[old_row_label][old_column_label]
            new_row_label = label_change_dict[old_row_label]
            new_column_label = label_change_dict[old_column_label]
            new_cayley_table_states.data[new_row_label][new_column_label] = outcome

    # TODO: check this gives the same as new_cayley_table_states.
    new_cayley_table_states2 = CayleyTableStates()
    new_cayley_table_states2.add_equiv_classes(
        equiv_classes=new_equiv_classes, initial_state=initial_state, world=world
    )

    return new_equiv_classes, new_cayley_table_states
