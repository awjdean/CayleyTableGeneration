import copy

from cayley_table_generation.cayley_table_states_main import (
    generate_cayley_table_states,
)
from cayley_table_states import CayleyTableStates
from equivalence_classes import EquivalenceClasses
from type_definitions import (
    CayleyTableActionsType,
    StateType,
)
from worlds.base_world import BaseWorld


class TransformationAlgebra:
    def __init__(self, name) -> None:
        self.name = name

        self._algebra_generation_parameters: dict

        # Cayley tables generation.
        self.cayley_table_states: CayleyTableStates
        self.cayley_table_actions: CayleyTableActionsType
        self.equiv_classes: EquivalenceClasses

    def generate_cayley_table_states(self, world: BaseWorld, initial_state):
        self.save_algebra_generation_paramenters(world, initial_state)
        self.cayley_table_states, self.equiv_classes = generate_cayley_table_states(
            world=world, initial_state=initial_state
        )

    def generate_cayley_table_actions(self):
        pass

    def save_cayley_tables(self):
        pass

    def load_cayley_tables(self):
        pass

    def save_algebra_generation_paramenters(
        self, world: BaseWorld, initial_state: StateType
    ):
        self._algebra_generation_parameters = {
            "world": copy.deepcopy(world),
            "initial_state": initial_state,
        }
