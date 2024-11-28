from cayley_table_generation.generate_initial_cayley_table_states import (
    generate_initial_cayley_table_states,
)
from cayley_table_states import CayleyTableStates
from equivalence_classes import EquivalenceClasses, generate_initial_equivalence_classes
from type_definitions import StateType
from worlds.base_world import BaseWorld


def generate_cayley_table_states(world: BaseWorld, initial_state: StateType):
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
    candidate_elements = search_for_candidate_elements(
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
        )


def search_for_candidate_elements(
    cayley_table_states: CayleyTableStates,
    initial_state: StateType,
    world: BaseWorld,
    equiv_classes: EquivalenceClasses,
):
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
