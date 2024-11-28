from cayley_table_generation.generate_initial_cayley_table_states import (
    generate_initial_cayley_table_states,
)
from equivalence_classes import generate_initial_equivalence_classes
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
    pass


def search_for_candidate_elements():
    candidate_elements = {}
