import copy
import os
import pickle

from cayley_tables.generators.actions_cayley_table_generator import (
    ActionsCayleyGenerator,
)
from cayley_tables.generators.states_cayley_table_generator import (
    StatesCayleyGenerator,
)
from cayley_tables.tables.cayley_table_actions import CayleyTableActions
from cayley_tables.tables.cayley_table_states import CayleyTableStates
from cayley_tables.utils.equiv_classes import EquivClasses
from NewAlgo.new_actions_cayley_generator import NewActionsCayleyGenerator
from NewAlgo.new_equiv_classes_generator import NewEquivClassGenerator
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
from utils.type_definitions import AlgebraGenerationMethod, StateType
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

    def generate(
        self,
        world: BaseWorld,
        initial_state: StateType | None = None,
        method: AlgebraGenerationMethod = AlgebraGenerationMethod.STATE_CAYLEY,
    ) -> None:
        """Generate the Cayley tables using the specified method.

        Args:
            world: The world to generate the algebra for
            initial_state: The initial state to start from (required for STATE_CAYLEY
              method)
            method: Which method to use for generation (defaults to STATE_CAYLEY)

        Raises:
            ValueError: If using STATE_CAYLEY method and initial_state is not provided
        """
        if method == AlgebraGenerationMethod.STATE_CAYLEY and initial_state is None:
            raise ValueError(
                "initial_state must be provided when using the STATE_CAYLEY generation"
                " method"
            )

        self._store_algebra_generation_paramenters(world, initial_state)  # type: ignore[arg-type]
        self._generation_method = method  # Store for use by other methods

        if method == AlgebraGenerationMethod.STATE_CAYLEY:
            self._generate_using_states_cayley(world, initial_state)  # type: ignore[arg-type]
        else:
            self._generate_using_action_function(world)

    def _generate_using_states_cayley(
        self, world: BaseWorld, initial_state: StateType
    ) -> None:
        """Generate using the original state Cayley table method."""
        # Generate states table and equiv classes
        self._states_cayley_generator = StatesCayleyGenerator(
            world=world, initial_state=initial_state
        )
        self.cayley_table_states, self.equiv_classes = (
            self._states_cayley_generator.generate()
        )

        # Generate actions table
        self._actions_cayley_generator = ActionsCayleyGenerator(self.equiv_classes)
        self.cayley_table_actions = self._actions_cayley_generator.generate()

    def _generate_using_action_function(self, world: BaseWorld) -> None:
        """Generate using the new action function method."""
        # Generate equiv classes using new method
        self._equiv_classes_generator = NewEquivClassGenerator(world)
        self._equiv_classes_generator.generate()
        self.equiv_classes = self._equiv_classes_generator.get_equiv_classes()

        # Generate actions Cayley table using new method
        self._actions_cayley_generator = NewActionsCayleyGenerator()
        self._actions_cayley_generator.generate(self._equiv_classes_generator)
        self.cayley_table_actions = (
            self._actions_cayley_generator.get_actions_cayley_table()
        )

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
            # Generation method
            "generation_method": getattr(self, "_generation_method", None),
            # Generators
            "states_cayley_generator": getattr(self, "_states_cayley_generator", None),
            "actions_cayley_generator": getattr(
                self, "_actions_cayley_generator", None
            ),
            "equiv_classes_generator": getattr(self, "_equiv_classes_generator", None),
            # Cayley tables and classes
            "equiv_classes": getattr(self, "equiv_classes", None),
            "cayley_table_actions": getattr(self, "cayley_table_actions", None),
            "cayley_table_states": (
                getattr(self, "cayley_table_states", None)
                if getattr(self, "_generation_method", None)
                == AlgebraGenerationMethod.STATE_CAYLEY
                else None
            ),
            # Generation parameters
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
        """Load the transformation algebra data from a pickle file."""
        if path is None:
            path = f"./saved/algebra/{self.name}.pkl"

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No saved algebra found at {path}. "
                "Generate and save the algebra first."
            )

        with open(path, "rb") as f:
            data = pickle.load(f)

        self._load_generation_data(data)
        self._load_tables_and_classes(data)
        self._load_algebraic_properties(data)

    def _load_generation_data(self, data: dict) -> None:
        """Load generation method and generators."""
        if "generation_method" in data:
            self._generation_method = data["generation_method"]
        if "states_cayley_generator" in data:
            self._states_cayley_generator = data["states_cayley_generator"]
        if "actions_cayley_generator" in data:
            self._actions_cayley_generator = data["actions_cayley_generator"]
        if "equiv_classes_generator" in data:
            self._equiv_classes_generator = data["equiv_classes_generator"]

    def _load_tables_and_classes(self, data: dict) -> None:
        """Load Cayley tables and equivalence classes."""
        if "equiv_classes" in data:
            self.equiv_classes = data["equiv_classes"]
        if "cayley_table_actions" in data:
            self.cayley_table_actions = data["cayley_table_actions"]
        if "cayley_table_states" in data and data["cayley_table_states"] is not None:
            self.cayley_table_states = data["cayley_table_states"]
        if "algebra_generation_parameters" in data:
            self._algebra_generation_parameters = data["algebra_generation_parameters"]

    def _load_algebraic_properties(self, data: dict) -> None:
        """Load algebraic properties."""
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
