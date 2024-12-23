import copy
import os
import pickle

from ActionFunctionsAlgo.generation.af_cayley_generator import AFCayleyGenerator
from ActionFunctionsAlgo.generation.af_equiv_classes_generator import (
    AFEquivClassGenerator,
)
from CayleyStatesAlgo.generation.actions_cayley_table_generator import (
    ActionsCayleyGenerator,
)
from CayleyStatesAlgo.generation.cayley_table_states import CayleyTableStates
from CayleyStatesAlgo.generation.states_cayley_table_generator import (
    StatesCayleyGenerator,
)
from LocalAlgebraAlgo.generation.local_cayley_generator import (
    LocalActionsCayleyGenerator,
)
from LocalAlgebraAlgo.generation.local_equiv_classes_generator import (
    LocalEquivClassGenerator,
)
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
from utils.cayley_table_actions import CayleyTableActions
from utils.equiv_classes import EquivClasses
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
        method: AlgebraGenerationMethod = AlgebraGenerationMethod.STATES_CAYLEY,
    ) -> None:
        """Generate the Cayley tables using the specified method.

        Args:
            world: The world to generate the algebra for
            initial_state: The initial state to start from (required for STATE_CAYLEY
             and LOCAL_ACTION_FUNCTION methods)
            method: Which method to use for generation (defaults to STATE_CAYLEY)

        Raises:
            ValueError: If using STATE_CAYLEY or LOCAL_ACTION_FUNCTION method and
             initial_state is not provided
        """
        if (
            method
            in [
                AlgebraGenerationMethod.STATES_CAYLEY,
                AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION,
            ]
            and initial_state is None
        ):
            raise ValueError(
                f"initial_state must be provided when using the {method} generation"
                " method"
            )

        self._store_algebra_generation_paramenters(world, initial_state)
        self._generation_method = method

        if method == AlgebraGenerationMethod.STATES_CAYLEY:
            self._generate_using_states_cayley(world, initial_state)  # type: ignore[arg-type]
        elif method == AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION:
            self._generate_using_local_action_function(world, initial_state)  # type: ignore[arg-type]
        elif method == AlgebraGenerationMethod.ACTION_FUNCTION:
            self._generate_using_action_function(world)
        else:
            raise ValueError(f"Invalid generation method: {method}")

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
        self._equiv_classes_generator = AFEquivClassGenerator(world)
        self._equiv_classes_generator.generate()
        self.equiv_classes = self._equiv_classes_generator.get_equiv_classes()

        # Generate actions Cayley table using new method
        self._actions_cayley_generator = AFCayleyGenerator()
        self._actions_cayley_generator.generate(self._equiv_classes_generator)
        self.cayley_table_actions = (
            self._actions_cayley_generator.get_actions_cayley_table()
        )

    def _generate_using_local_action_function(
        self, world: BaseWorld, initial_state: StateType
    ) -> None:
        """Generate using the local action function method."""

        # Generate equiv classes using local method
        self._equiv_classes_generator = LocalEquivClassGenerator(world)
        self._equiv_classes_generator.generate(initial_state)
        self.equiv_classes = self._equiv_classes_generator.get_equiv_classes()

        # Generate actions Cayley table using local method
        self._actions_cayley_generator = LocalActionsCayleyGenerator()
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
                == AlgebraGenerationMethod.STATES_CAYLEY
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
        self, world: BaseWorld, initial_state: StateType | None
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

    def print_properties(self, details: bool = False) -> None:
        """Print all algebraic properties in a formatted way."""
        print(f"\n{self.name} Results")
        print("=" * (len(self.name) + 8))

        if details:
            self._print_detailed_properties()
        else:
            self._print_summary_properties()
        print("")

    def _print_detailed_properties(self) -> None:
        """Print detailed property information."""
        if hasattr(self, "cayley_table_actions"):
            print("\nCayley Table:")
            print(self.cayley_table_actions)

        print("\nAlgebraic Properties:")
        print("-" * 20)

        self._print_associativity_details()
        self._print_identity_details()
        self._print_inverse_details()
        self._print_commutativity_details()
        self._print_element_orders_details()

    def _print_summary_properties(self) -> None:
        """Print summary of properties."""
        print("\nProperties:")
        print(
            f"{'Associative':12}"
            f" {getattr(self, 'associativity_info', {}).get(
                'is_associative_algebra', '-')
                }"
        )
        print(
            f"{'Identity':12}"
            f" {getattr(self, 'identity_info', {}).get('is_identity_algebra', '-')}"
        )
        print(
            f"{'Inverses':12}"
            f" {getattr(self, 'inverse_info', {}).get('is_inverse_algebra', '-')}"
        )
        print(
            f"{'Commutative':12}"
            f" {getattr(self, 'commutativity_info', {}).get(
                'is_commutative_algebra', '-'
                )}"
        )

    def _print_associativity_details(self) -> None:
        """Print detailed associativity information."""
        print("\nAssociativity:")
        for k, v in getattr(self, "associativity_info", {"-": "-"}).items():
            if k == "violations" and v:
                print(f"  {k}:")
                for violation in v:
                    print(f"    {violation}")
            else:
                print(f"  {k}: {v}")

    def _print_identity_details(self) -> None:
        """Print detailed identity information."""
        print("\nIdentity:")
        for k, v in getattr(self, "identity_info", {"-": "-"}).items():
            print(f"  {k}: {v}")

    def _print_inverse_details(self) -> None:
        """Print detailed inverse information."""
        print("\nInverses:")
        inverse_info = getattr(self, "inverse_info", {"-": "-"})
        if isinstance(inverse_info, dict):
            print(
                f"  is_inverse_algebra: {inverse_info.get('is_inverse_algebra', '-')}"
            )
            for k, v in inverse_info.items():
                if k == "is_inverse_algebra":
                    continue
                print(f"  {k}:")
                if isinstance(v, dict):
                    for element, pairs in v.items():
                        print(f"    {element}:")
                        for pair in pairs:
                            print(f"      {pair}")
                else:
                    print(f"    {v}")
        else:
            print(f"  {inverse_info}")

    def _print_commutativity_details(self) -> None:
        """Print detailed commutativity information."""
        print("\nCommutativity:")
        comm_info = getattr(self, "commutativity_info", {"-": "-"})
        if isinstance(comm_info, dict):
            print(
                f"  is_commutative_algebra: {comm_info.get(
                    'is_commutative_algebra', '-'
                    )}"
            )
            print(f"  commute_with_all: {comm_info.get('commute_with_all', '-')}")

            if "commuting_elements" in comm_info:
                print("  commuting_elements:")
                for element, commutes_with in comm_info["commuting_elements"].items():
                    print(f"    {element}: {commutes_with}")

            if "non_commuting_elements" in comm_info:
                print("  non_commuting_elements:")
                for element, non_commutes_with in comm_info[
                    "non_commuting_elements"
                ].items():
                    print(f"    {element}: {non_commutes_with}")
        else:
            print(f"  {comm_info}")

    def _print_element_orders_details(self) -> None:
        """Print detailed element order information."""
        print("\nElement Orders:")
        orders = getattr(self, "element_orders", {"-": "-"})
        if isinstance(orders, dict) and "orders" in orders:
            for element, info in orders["orders"].items():
                print(f"  {element}: {info}")
        else:
            print(f"  {orders}")
