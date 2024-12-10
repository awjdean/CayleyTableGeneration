import copy

from cayley_tables.cayley_table_actions import (
    CayleyTableActions,
    generate_cayley_table_actions,
)
from cayley_tables.cayley_table_states import CayleyTableStates
from cayley_tables.equiv_classes import EquivClasses
from cayley_tables.states_cayley_table_generation.generate_cayley_table_states import (
    generate_cayley_table_states_and_equiv_classes,
)
from utils.type_definitions import (
    StateType,
)
from worlds.base_world import BaseWorld


class TransformationAlgebra:
    def __init__(self, name) -> None:
        self.name = name

        self._algebra_generation_parameters: dict

        # Cayley tables generation.
        self.cayley_table_states: CayleyTableStates
        self.cayley_table_actions: CayleyTableActions
        self.equiv_classes: EquivClasses

    def generate_cayley_table_states(self, world: BaseWorld, initial_state):
        self.store_algebra_generation_paramenters(world, initial_state)
        self.cayley_table_states, self.equiv_classes = (
            generate_cayley_table_states_and_equiv_classes(
                world=world, initial_state=initial_state
            )
        )
        # self.equiv_classes, self.cayley_table_states = (
        #     relabel_equiv_classes_and_state_cayley_table(
        #         equiv_classes=self.equiv_classes,
        #         cayley_table_states=self.cayley_table_states,
        #         initial_state=initial_state,
        #         world=world,
        #     )
        # )

    def generate_cayley_table_actions(self):
        if not hasattr(self, "equiv_classes") or self.equiv_classes is None:
            raise ValueError(
                "equiv_classes must be generated before generating Cayley table"
                "actions. Call generate_cayley_table_states() first."
            )
        self.cayley_table_actions = generate_cayley_table_actions(self.equiv_classes)

    def save_cayley_tables(self):
        pass

    def load_cayley_tables(self):
        pass

    def store_algebra_generation_paramenters(
        self, world: BaseWorld, initial_state: StateType
    ):
        self._algebra_generation_parameters = {
            "world": copy.deepcopy(world),
            "initial_state": initial_state,
        }
