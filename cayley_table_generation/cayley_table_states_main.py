from cayley_table_generation.generate_initial_cayley_table_states import (
    generate_initial_cayley_table_states,
)
from cayley_table_generation.helpers import generate_action_sequence_outcome
from cayley_table_states import CayleyTableStates
from equiv_classes import EquivClasses, generate_initial_equivalence_classes
from type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


def generate_cayley_table_states(
    world: BaseWorld, initial_state: StateType
) -> tuple[CayleyTableStates, EquivClasses]:
    # Initialise variables.
    min_actions = world.get_min_actions()

    # Generate initial equivalence classes.
    equiv_classes = generate_initial_equivalence_classes(
        min_actions, initial_state, world
    )

    # Generate initial states Cayley table.
    cayley_table_states = generate_initial_cayley_table_states(
        equiv_class_labels=equiv_classes.get_labels(),
        initial_state=initial_state,
        world=world,
    )

    # Search for candidate elements.
    candidate_elements = find_candidate_elements(
        cayley_table_states=cayley_table_states,
        initial_state=initial_state,
        world=world,
        equiv_classes=equiv_classes,
    )

    while len(candidate_elements) > 0:
        candidate_element = candidate_elements.pop()
        # Check if candidate element is in an existing equivalence class.
        equiv_elements = cayley_table_states.find_equiv_elements(
            element=candidate_element,
            initial_state=initial_state,
            world=world,
            take_first=True,
        )
        # If candidate_element is in an existing equivalence class, add it to the class
        # and move to next candidate_element.
        if len(equiv_elements):
            equiv_element_label = next(iter(equiv_elements.keys()))
            equiv_classes.add_element(
                element=candidate_element, class_label=equiv_element_label
            )
            continue

        # Check if candidate_element breaks any existing equivalence classes.
        new_equiv_classes = find_broken_equiv_classes(
            candidate_element=candidate_element,
            equiv_classes=equiv_classes,
            initial_state=initial_state,
            world=world,
        )

        # Remove elements in new_equiv_classes from equiv_classes.
        equiv_classes.remove_elements_from_classes(
            elements=new_equiv_classes.get_all_elements()
        )

        # Create equiv class in new_equiv_classes for candidate_element.
        new_equiv_classes.create_new_class(
            class_label=candidate_element,
            outcome=generate_action_sequence_outcome(
                action_sequence=candidate_element,
                initial_state=initial_state,
                world=world,
            ),
        )

        # Merge new_equiv_classes into equiv_classes.
        equiv_classes.merge_equiv_class_instances(new_equiv_classes)

        # Add new_equiv_classes to cayley_table_states.
        cayley_table_states.add_equiv_classes(new_equiv_classes, initial_state, world)

        # Search for new candidate elements.
        if len(candidate_elements) == 0:
            candidate_elements = find_candidate_elements(
                cayley_table_states=cayley_table_states,
                initial_state=initial_state,
                world=world,
                equiv_classes=equiv_classes,
            )

    return cayley_table_states, equiv_classes


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
    b_label_outcome = generate_action_sequence_outcome(
        action_sequence=b_label + candidate_element,
        initial_state=initial_state,
        world=world,
    )

    for b_element in equiv_classes.get_class_elements(b_label):
        # Calculate: b_element * (candidate_element * w_{0}).
        b_element_outcome = generate_action_sequence_outcome(
            action_sequence=b_element + candidate_element,
            initial_state=initial_state,
            world=world,
        )
        # If b_label * (candidate_element * w_{0}) != b_element * (candidate_element
        # * w_{0}), then b_element should be in a different equiv class to b_label
        # (candidate_element has broken the equiv class labelled by b_label).
        if b_label_outcome != b_element_outcome:
            for c_label in new_equiv_classes.get_labels():
                # Calculate: c_label * (candidate_element * w_{0}).
                c_outcome = generate_action_sequence_outcome(
                    action_sequence=c_label + candidate_element,
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


def find_candidate_elements(
    cayley_table_states: CayleyTableStates,
    initial_state: StateType,
    world: BaseWorld,
    equiv_classes: EquivClasses,
) -> set[ActionType]:
    candidate_elements = set()
    for row_label in cayley_table_states.get_row_labels():
        for col_label in cayley_table_states.get_row_labels():
            candidate_element = col_label + row_label
            equiv_elements = cayley_table_states.find_equiv_elements(
                element=candidate_element,
                initial_state=initial_state,
                world=world,
            )
            if len(equiv_elements) == 1:
                equiv_element_label = next(iter(equiv_elements.keys()))
                equiv_classes.add_element(
                    element=candidate_element, class_label=equiv_element_label
                )
            elif len(equiv_elements) == 0:
                candidate_elements.add(candidate_element)
            else:
                raise ValueError(
                    "Candidate element is in multiple equivalence classes."
                )
    return candidate_elements
