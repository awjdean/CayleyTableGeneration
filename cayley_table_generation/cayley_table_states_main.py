from cayley_table_generation.action_outcome import generate_action_outcome
from cayley_table_generation.breaking_equiv_classes import find_broken_equiv_classes
from cayley_table_generation.candidate_elements import find_candidate_elements
from cayley_table_generation.cayley_table_states import CayleyTableStates
from cayley_table_generation.equiv_classes import (
    EquivClasses,
    generate_initial_equivalence_classes,
)
from cayley_table_generation.initial_cayley_table_states import (
    generate_initial_cayley_table_states,
)
from type_definitions import StateType
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
            outcome=generate_action_outcome(
                action=candidate_element,
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
