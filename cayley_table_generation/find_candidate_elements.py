from cayley_table_generation.cayley_table_states import CayleyTableStates
from cayley_table_generation.equiv_classes import EquivClasses
from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld


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
