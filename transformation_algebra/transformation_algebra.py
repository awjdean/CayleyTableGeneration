import copy
import os
import pickle

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
        self._store_algebra_generation_paramenters(world, initial_state)
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

    def save(self, path: str | None) -> None:
        """Save the transformation algebra data to a pickle file.

        Args:
            path: Optional path where the pickle file should be saved.
                 If None, saves to ./saved/algebra/{name}.pkl
        """
        if path is None:
            # Create directory if it doesn't exist
            os.makedirs("./saved/algebra/", exist_ok=True)
            path = f"./saved/algebra/{self.name}.pkl"

        data = {
            "cayley_table_states": getattr(self, "cayley_table_states", None),
            "cayley_table_actions": getattr(self, "cayley_table_actions", None),
            "equiv_classes": getattr(self, "equiv_classes", None),
            "algebra_generation_parameters": getattr(
                self, "_algebra_generation_parameters", None
            ),
        }

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str | None = None) -> None:
        """Load the transformation algebra data from a pickle file.

        Args:
            path: Optional path to the pickle file.
                 If None, loads from ./saved/algebra/{name}.pkl
        """
        if path is None:
            path = f"./saved/algebra/{self.name}.pkl"

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No saved algebra found at {path}. "
                "Generate and save the algebra first."
            )

        with open(path, "rb") as f:
            data = pickle.load(f)

        # Load the attributes if they exist in the saved data
        if "cayley_table_states" in data:
            self.cayley_table_states = data["cayley_table_states"]

        if "cayley_table_actions" in data:
            self.cayley_table_actions = data["cayley_table_actions"]

        if "equiv_classes" in data:
            self.equiv_classes = data["equiv_classes"]

        if "algebra_generation_parameters" in data:
            self._algebra_generation_parameters = data["algebra_generation_parameters"]

    def _store_algebra_generation_paramenters(
        self, world: BaseWorld, initial_state: StateType
    ):
        self._algebra_generation_parameters = {
            "world": copy.deepcopy(world),
            "initial_state": initial_state,
        }
