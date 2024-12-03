import pandas as pd

from cayley_table_generation.cayley_table_states import CayleyTableStates
from cayley_table_generation.equiv_classes import EquivClasses
from utils.type_definitions import ActionType, CayleyTableActionsDataType, StateType
from worlds.base_world import BaseWorld


class CayleyTableActions:
    def __init__(self):
        self.data: CayleyTableActionsDataType = {}

    def __str__(self):
        if not self.data:
            return "\nCayleyTableActions = {}"
        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")
        # Return the string representation of the DataFrame
        return f"\nCayleyTableActions =\n{df}"


def generate_cayley_table_actions(equiv_classes: EquivClasses) -> CayleyTableActions:
    # Create cayley_table_actions.
    cayley_table_actions = CayleyTableActions()

    # Fill cayley_table_actions.
    ## For each entry in cayley_table_actions:
    for row_label in equiv_classes.get_labels():
        # Initialise rows.
        cayley_table_actions.data[row_label] = {}
        for column_label in equiv_classes.get_labels():
            action = column_label + row_label
            outcome_class_label = equiv_classes.find_element_class(action)
            if outcome_class_label is None:
                # TODO: Make this raise more informative.
                # This should only be hit if relabelling has happened.
                print(f"Action '{action}' not found in any equivalence class.")
                # Find action using world OR write equiv_classes function to reduce an
                #  action sequence to a class_labelling element.
                raise Exception("")

            cayley_table_actions.data[row_label][column_label] = outcome_class_label

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
        # Create new row in new new_cayley_table_states.
        new_row_label = label_change_dict[old_row_label]
        new_cayley_table_states.data[new_row_label] = {}
        for old_column_label in equiv_classes.get_labels():
            # Get outcome from old cayley_table_states.
            outcome = cayley_table_states.data[old_row_label][old_column_label]
            new_column_label = label_change_dict[old_column_label]
            new_cayley_table_states.data[new_row_label][new_column_label] = outcome

    # TODO: Remove this.
    new_cayley_table_states2 = CayleyTableStates()
    new_cayley_table_states2.add_equiv_classes(
        equiv_classes=new_equiv_classes, initial_state=initial_state, world=world
    )
    if new_cayley_table_states.data != new_cayley_table_states2.data:
        raise Exception("")

    return new_equiv_classes, new_cayley_table_states
