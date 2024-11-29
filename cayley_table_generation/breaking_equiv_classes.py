from cayley_table_generation.action_outcome import generate_action_outcome
from cayley_table_generation.equiv_classes import EquivClasses
from type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


def find_broken_equiv_classes(
    candidate_element: ActionType,
    equiv_classes: EquivClasses,
    initial_state: StateType,
    world: BaseWorld,
):
    new_equiv_classes = EquivClasses()
    for class_label in equiv_classes.get_labels():
        # Check if candidate_element breaks the equiv class labelled by class_label.
        temp_new_equivs = check_if_equiv_class_broken(
            candidate_element=candidate_element,
            b_label=class_label,
            equiv_classes=equiv_classes,
            initial_state=initial_state,
            world=world,
        )
        new_equiv_classes.merge_equiv_class_instances(temp_new_equivs)

    return new_equiv_classes


def check_if_equiv_class_broken(
    candidate_element: ActionType,
    b_label: ActionType,
    equiv_classes: EquivClasses,
    initial_state: StateType,
    world: BaseWorld,
):
    """
    Checks if the candidate element breaks the equivalence class labelled by b_label.
    """
    new_equiv_classes = EquivClasses()
    if len(equiv_classes.get_class_elements(b_label)) == 1:
        return new_equiv_classes

    # Calculate: b_label * (candidate_element * w_{0}).
    b_label_outcome = generate_action_outcome(
        action=b_label + candidate_element,
        initial_state=initial_state,
        world=world,
    )

    for b_element in equiv_classes.get_class_elements(b_label):
        # Calculate: b_element * (candidate_element * w_{0}).
        b_element_outcome = generate_action_outcome(
            action=b_element + candidate_element,
            initial_state=initial_state,
            world=world,
        )
        # If b_label * (candidate_element * w_{0}) != b_element * (candidate_element
        # * w_{0}), then b_element should be in a different equiv class to b_label
        # (candidate_element has broken the equiv class labelled by b_label).
        if b_label_outcome != b_element_outcome:
            for c_label in new_equiv_classes.get_labels():
                # Calculate: c_label * (candidate_element * w_{0}).
                c_outcome = generate_action_outcome(
                    action=c_label + candidate_element,
                    initial_state=initial_state,
                    world=world,
                )

                # If b_element * (candidate_element * w_{0}) = c_label *
                # (candidate_element * w_{0}), then b_element is in b_element's equiv
                #  class.
                if b_element_outcome == c_outcome:
                    new_equiv_classes.add_element(
                        element=b_element, class_label=c_label
                    )
                    break
            # If b_element not in any existing new equiv class, then create new equiv
            # class with b_element as label.
            else:
                # TODO: check this.
                new_equiv_outcome = equiv_classes.get_class_outcome(b_label)
                new_equiv_classes.create_new_class(
                    class_label=b_element, outcome=new_equiv_outcome
                )
    return new_equiv_classes
