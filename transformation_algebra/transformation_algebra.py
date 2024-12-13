import copy
import os
import pickle

from cayley_tables.actions_cayley_table_generator import ActionsCayleyTableGenerator
from cayley_tables.cayley_table_actions import (
    CayleyTableActions,
)
from cayley_tables.cayley_table_states import CayleyTableStates
from cayley_tables.equiv_classes import EquivClasses
from cayley_tables.states_cayley_table_generator import StatesCayleyTableGenerator
from transformation_algebra.property_checkers.associativity import (
    AssociativityResultType,
    check_associativity,
)
from transformation_algebra.property_checkers.commutativity import (
    CommutativityResultType,
    check_commutativity,
)
from transformation_algebra.property_checkers.elements_order import (
    ElementOrderResultType,
    calculate_element_orders,
)
from transformation_algebra.property_checkers.identity import (
    IdentityResultType,
    check_identity,
)
from transformation_algebra.property_checkers.inverse import (
    InverseResultsType,
    check_inverse,
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

        # Algebraic properties
        self.associativity_info: AssociativityResultType
        self.identity_info: IdentityResultType
        self.inverse_info: InverseResultsType
        self.element_orders: ElementOrderResultType
        self.commutativity_info: CommutativityResultType

    def generate_cayley_table_states(
        self, world: BaseWorld, initial_state: StateType
    ) -> None:
        self._store_algebra_generation_paramenters(world, initial_state)

        generator = StatesCayleyTableGenerator(world=world, initial_state=initial_state)

        self.cayley_table_states, self.equiv_classes = generator.generate()

    def generate_cayley_table_actions(self):
        if not hasattr(self, "equiv_classes") or self.equiv_classes is None:
            raise ValueError(
                "equiv_classes must be generated before generating Cayley table"
                "actions. Call generate_cayley_table_states() first."
            )
        generator = ActionsCayleyTableGenerator(self.equiv_classes)
        self.cayley_table_actions = generator.generate()

    def save(self, path: str | None) -> None:
        """Save the transformation algebra data to a pickle file.

        Args:
            path: Optional path where the pickle file should be saved.
                 If None, saves to ./saved/algebra/{name}.pkl
        """
        if path is None:
            os.makedirs("./saved/algebra/", exist_ok=True)
            path = f"./saved/algebra/{self.name}.pkl"

        data = {
            # Cayley tables
            "cayley_table_states": getattr(self, "cayley_table_states", None),
            "cayley_table_actions": getattr(self, "cayley_table_actions", None),
            "equiv_classes": getattr(self, "equiv_classes", None),
            "algebra_generation_parameters": getattr(
                self, "_algebra_generation_parameters", None
            ),
            # Algebraic properties
            "associativity_info": getattr(self, "associativity_info", None),
            "identity_info": getattr(self, "identity_info", None),
            "inverse_info": getattr(self, "inverse_info", None),
            "element_orders": getattr(self, "element_orders", None),
            "commutativity_info": getattr(self, "commutativity_info", None),
        }

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

        # Load Cayley tables
        if "cayley_table_states" in data:
            self.cayley_table_states = data["cayley_table_states"]
        if "cayley_table_actions" in data:
            self.cayley_table_actions = data["cayley_table_actions"]
        if "equiv_classes" in data:
            self.equiv_classes = data["equiv_classes"]
        if "algebra_generation_parameters" in data:
            self._algebra_generation_parameters = data["algebra_generation_parameters"]

        # Load algebraic properties
        if "associativity_info" in data:
            self.associativity_info = data["associativity_info"]
        if "identity_info" in data:
            self.identity_info = data["identity_info"]
        if "inverse_info" in data:
            self.inverse_info = data["inverse_info"]
        if "element_orders" in data:
            self.element_orders = data["element_orders"]
        if "commutativity_info" in data:
            self.commutativity_info = data["commutativity_info"]

    def _store_algebra_generation_paramenters(
        self, world: BaseWorld, initial_state: StateType
    ):
        self._algebra_generation_parameters = {
            "world": copy.deepcopy(world),
            "initial_state": initial_state,
        }

    def check_properties(self) -> None:
        """Check all algebraic properties and store results."""
        if not hasattr(self, "cayley_table_actions"):
            raise ValueError(
                "Cayley table must be generated before checking properties. "
                "Call generate_cayley_table_actions() first."
            )

        # Compute properties in order, validating each result
        self.associativity_info = check_associativity(self.cayley_table_actions)
        if self.associativity_info is None:
            raise ValueError("Failed to compute associativity")

        self.identity_info = check_identity(self.cayley_table_actions)
        if self.identity_info is None:
            raise ValueError("Failed to compute identity elements")

        self.inverse_info = check_inverse(self.cayley_table_actions, self.identity_info)
        if self.inverse_info is None:
            raise ValueError("Failed to compute inverses")

        self.element_orders = calculate_element_orders(
            self.cayley_table_actions, self.identity_info
        )
        if self.element_orders is None:
            raise ValueError("Failed to compute element orders")

        self.commutativity_info = check_commutativity(self.cayley_table_actions)
        if self.commutativity_info is None:
            raise ValueError("Failed to compute commutativity")
