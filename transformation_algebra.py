import copy

from cayley_table_generation.cayley_table_states_main import (
    generate_cayley_table_states,
)
from type_definitions import (
    CayleyTableActionsType,
    CayleyTableStatesType,
    EquivalenceClassesType,
)
from worlds.base_world import BaseWorld


class TransformationAlgebra:
    def __init__(self, name) -> None:
        self.name = name

        self._algebra_generation_parameters = None
        # Cayley tables generation.
        # TODO: Have a cayley_table class with these as properties ?
        self.cayley_table_states: CayleyTableStatesType | None = None
        self.cayley_table_actions: CayleyTableActionsType | None = None
        self.equivalence_classes: EquivalenceClassesType | None = None

    def generate_cayley_table_states(self, world: BaseWorld, initial_state):
        self.save_algebra_generation_paramenters(world, initial_state)
        generate_cayley_table_states(world=world, initial_state=initial_state)

    def generate_cayley_table_actions(self):
        pass

    def save_cayley_tables(self):
        pass

    def load_cayley_tables(self):
        pass

    def save_algebra_generation_paramenters(self, world, initial_state):
        self._algebra_generation_parameters = {
            "world": copy.deepcopy(world),
            "initial_state": initial_state,
        }
