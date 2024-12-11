from dataclasses import dataclass
from typing import TypedDict

from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.type_definitions import ActionType


@dataclass
class IsomorphismMap:
    """Represents an isomorphism between two transformation algebras."""

    mapping: dict[ActionType, ActionType]  # Maps elements from A₁ to A₂


class IsomorphismResult(TypedDict):
    """Result of checking if two transformation algebras are isomorphic."""

    is_isomorphic: bool
    reason: str | None  # Reason why algebras aren't isomorphic, if they aren't
    mapping: IsomorphismMap | None  # Isomorphism if one exists
    mapping_str: str | None  # Formatted string representation of the mapping


def check_isomorphism(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> IsomorphismResult:
    """Check if two transformation algebras are isomorphic.

    Two algebras are isomorphic if there exists a bijective map φ: A₁ → A₂
    that preserves the algebraic structure: φ(x * y) = φ(x) * φ(y).

    Args:
        algebra1: First transformation algebra
        algebra2: Second transformation algebra

    Returns:
        IsomorphismResult containing:
        - is_isomorphic: True if algebras are isomorphic
        - reason: Why algebras aren't isomorphic (if they aren't)
        - mapping: The isomorphism map (if one exists)
    """
    # Ensure properties have been computed
    try:
        algebra1.check_properties()
        algebra2.check_properties()
    except ValueError as e:
        return {
            "is_isomorphic": False,
            "reason": f"Property check failed: {e!s}",
            "mapping": None,
            "mapping_str": None,
        }

    # First check basic properties that must match
    print("\tChecking basic properties...")
    basic_check = _check_basic_properties(algebra1, algebra2)
    if not basic_check[0]:
        return {
            "is_isomorphic": False,
            "reason": basic_check[1],
            "mapping": None,
            "mapping_str": None,
        }
    print("\tBasic property checks passed.")

    # Get the constraints for possible mappings
    print("\tCollecting mapping constraints...")
    constraints = _get_mapping_constraints(algebra1, algebra2)
    print("\tMapping constraints collected.")

    # Try all possible mappings that satisfy the constraints
    print("\tCalculating possible mappings...")
    possible_mappings = _generate_candidate_mappings(algebra1, algebra2, constraints)
    print(f"\tPossible mappings: {len(possible_mappings)}")
    for mapping in possible_mappings:
        if _is_homomorphism(algebra1, algebra2, mapping):
            return {
                "is_isomorphic": True,
                "reason": None,
                "mapping": IsomorphismMap(mapping=mapping),
                "mapping_str": _format_mapping(mapping),
            }

    return {
        "is_isomorphic": False,
        "reason": "No valid isomorphism exists that preserves the algebraic structure",
        "mapping": None,
        "mapping_str": None,
    }


def _check_basic_properties(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> tuple[bool, str | None]:
    """Check if basic properties match between two algebras.

    Checks:
    1. Cardinality (number of elements)
    2. Associativity
    3. Identity elements (two-sided, left, and right)

    Args:
        algebra1: First transformation algebra
        algebra2: Second transformation algebra

    Returns:
        Tuple containing:
        - bool: True if all basic properties match
        - str: Reason for mismatch if properties don't match, None otherwise
    """
    # Check cardinality
    elements1 = set(algebra1.cayley_table_actions.get_row_labels())
    elements2 = set(algebra2.cayley_table_actions.get_row_labels())
    if len(elements1) != len(elements2):
        return False, (
            f"Algebras have different sizes: |A₁| = {len(elements1)}, "
            f"|A₂| = {len(elements2)}"
        )

    # Check associativity
    if (
        algebra1.associativity_info["is_associative_algebra"]
        != algebra2.associativity_info["is_associative_algebra"]
    ):
        algebra1_print_str = (
            "is" if algebra1.associativity_info["is_associative_algebra"] else "is not"
        )
        algebra2_print_str = (
            "is" if algebra2.associativity_info["is_associative_algebra"] else "is not"
        )
        return False, (
            "One algebra is associative while the other is not: "
            f"A₁ {algebra1_print_str} associative, "
            f"A₂ {algebra2_print_str} associative"
        )

    # Check identity elements
    if (
        algebra1.identity_info["is_identity_algebra"]
        != algebra2.identity_info["is_identity_algebra"]
    ):
        algebra1_print_str = (
            "has" if algebra1.identity_info["is_identity_algebra"] else "does not have"
        )
        algebra2_print_str = (
            "has" if algebra2.identity_info["is_identity_algebra"] else "does not have"
        )
        return False, (
            "One algebra has an identity while the other does not: "
            f"A₁ {algebra1_print_str} an"
            f" identity, A₂ {algebra2_print_str}"
            " an identity"
        )

    # Check left identities
    if len(algebra1.identity_info["left_identities"]) != len(
        algebra2.identity_info["left_identities"]
    ):
        return False, (
            "Algebras have different numbers of left identities: "
            f"A₁ has {len(algebra1.identity_info['left_identities'])}, "
            f"A₂ has {len(algebra2.identity_info['left_identities'])}"
        )

    # Check right identities
    if len(algebra1.identity_info["right_identities"]) != len(
        algebra2.identity_info["right_identities"]
    ):
        return False, (
            "Algebras have different numbers of right identities: "
            f"A₁ has {len(algebra1.identity_info['right_identities'])}, "
            f"A₂ has {len(algebra2.identity_info['right_identities'])}"
        )

    return True, None


def _get_mapping_constraints(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> dict[ActionType, set[ActionType]]:
    """Get constraints on possible element mappings."""
    constraints = _init_basic_constraints(algebra1, algebra2)
    constraints = _apply_identity_constraints(algebra1, algebra2, constraints)
    constraints = _apply_order_constraints(algebra1, algebra2, constraints)
    constraints = _apply_commutativity_constraints(algebra1, algebra2, constraints)
    constraints = _apply_inverse_constraints(algebra1, algebra2, constraints)
    return constraints


def _init_basic_constraints(algebra1, algebra2):
    elements1 = set(algebra1.cayley_table_actions.get_row_labels())
    elements2 = set(algebra2.cayley_table_actions.get_row_labels())
    return {a: elements2.copy() for a in elements1}


def _apply_identity_constraints(
    algebra1: TransformationAlgebra,
    algebra2: TransformationAlgebra,
    constraints: dict[ActionType, set[ActionType]],
) -> dict[ActionType, set[ActionType]]:
    """Apply constraints based on identity elements."""
    if algebra1.identity_info["is_identity_algebra"]:
        # Two-sided identities must map to each other
        e1 = algebra1.identity_info["identities"][0]
        e2 = algebra2.identity_info["identities"][0]
        constraints[e1] = {e2}

        # Left identities must map to left identities
        left_ids2 = set(algebra2.identity_info["left_identities"])
        for a in algebra1.identity_info["left_identities"]:
            constraints[a] &= left_ids2

        # Right identities must map to right identities
        right_ids2 = set(algebra2.identity_info["right_identities"])
        for a in algebra1.identity_info["right_identities"]:
            constraints[a] &= right_ids2

    return constraints


def _apply_order_constraints(
    algebra1: TransformationAlgebra,
    algebra2: TransformationAlgebra,
    constraints: dict[ActionType, set[ActionType]],
) -> dict[ActionType, set[ActionType]]:
    """Apply constraints based on element orders."""
    # Group elements by order for efficient lookup
    elements_by_order2 = {}
    for b in algebra2.cayley_table_actions.get_row_labels():
        order = algebra2.element_orders["orders"][b].order
        if order not in elements_by_order2:
            elements_by_order2[order] = set()
        elements_by_order2[order].add(b)

    # Apply order constraints
    for a in algebra1.cayley_table_actions.get_row_labels():
        order_a = algebra1.element_orders["orders"][a].order
        if order_a in elements_by_order2:
            constraints[a] &= elements_by_order2[order_a]
        else:
            constraints[a] = set()

    return constraints


def _apply_commutativity_constraints(
    algebra1: TransformationAlgebra,
    algebra2: TransformationAlgebra,
    constraints: dict[ActionType, set[ActionType]],
) -> dict[ActionType, set[ActionType]]:
    """Apply constraints based on commutativity."""
    # Elements that commute with all must map to elements that commute with all
    commute_all2 = set(algebra2.commutativity_info["commute_with_all"])
    for a in algebra1.commutativity_info["commute_with_all"]:
        constraints[a] &= commute_all2

    # Elements must map to elements with same commuting structure
    for a in algebra1.cayley_table_actions.get_row_labels():
        num_commuting_a = len(algebra1.commutativity_info["commuting_elements"][a])
        constraints[a] &= {
            b
            for b in constraints[a]
            if len(algebra2.commutativity_info["commuting_elements"][b])
            == num_commuting_a
        }

    return constraints


def _apply_inverse_constraints(
    algebra1: TransformationAlgebra,
    algebra2: TransformationAlgebra,
    constraints: dict[ActionType, set[ActionType]],
) -> dict[ActionType, set[ActionType]]:
    """Apply constraints based on inverses."""
    if not algebra1.identity_info["is_identity_algebra"]:
        return constraints

    # Initialize mapping with known identity element mappings
    mapping = {
        e1: e2
        for e1, e2 in zip(
            algebra1.identity_info["identities"],
            algebra2.identity_info["identities"],
        )
    }

    # Apply left, right, and two-sided inverse constraints
    for inverse_type in ["left_inverses", "right_inverses", "inverses"]:
        for a in algebra1.inverse_info[inverse_type]:
            for pair in algebra1.inverse_info[inverse_type][a]:
                b, e = pair.inverse, pair.identity
                for possible_a_prime in constraints[a]:
                    constraints[b] &= {
                        b_prime
                        for b_prime in constraints[b]
                        if any(
                            p.inverse == b_prime and p.identity == mapping[e]
                            for p in algebra2.inverse_info[inverse_type].get(
                                possible_a_prime, []
                            )
                        )
                    }

    return constraints


def _generate_candidate_mappings(
    algebra1: TransformationAlgebra,
    algebra2: TransformationAlgebra,
    constraints: dict[ActionType, set[ActionType]],
) -> list[dict[ActionType, ActionType]]:
    """Generate all possible bijective mappings that satisfy the constraints.

    Uses the constraints to generate candidate isomorphisms φ: A₁ → A₂.
    Each mapping must be bijective (one-to-one and onto) and satisfy all
    constraints on which elements can map to which.

    Args:
        algebra1: First transformation algebra
        algebra2: Second transformation algebra
        constraints: Dict mapping each element of A₁ to its allowed images in A₂

    Returns:
        List of dicts, each representing a possible bijective mapping from A₁ to A₂

    Note:
        If any element has no valid mappings (empty constraint set), returns empty list
        as no valid bijective mapping can exist.
    """
    elements1 = algebra1.cayley_table_actions.get_row_labels()
    elements2 = set(algebra2.cayley_table_actions.get_row_labels())

    # Verify we have same number of elements (needed for bijectivity)
    if len(elements1) != len(elements2):
        return []

    # If any element has no possible mappings, no valid bijection exists
    if any(not allowed for allowed in constraints.values()):
        return []

    # Start with elements that have only one possible mapping
    fixed_mappings = {
        a: next(iter(allowed))
        for a, allowed in constraints.items()
        if len(allowed) == 1
    }

    # Remove fixed mappings from constraints and track used elements
    remaining_constraints = {}
    used_elements2 = set(fixed_mappings.values())

    for a in elements1:
        if a not in fixed_mappings:
            # Remove already used elements from possible mappings
            valid_mappings = constraints[a] - used_elements2
            if not valid_mappings:  # No valid mappings left
                return []
            remaining_constraints[a] = valid_mappings

    # Generate all possible combinations for remaining elements
    candidate_mappings = []

    def extend_mapping(
        current_mapping: dict[ActionType, ActionType],
        remaining: dict[ActionType, set[ActionType]],
        used: set[ActionType],
    ) -> None:
        if not remaining:  # All elements mapped
            candidate_mappings.append(current_mapping.copy())
            return

        # Pick next element to map
        a = min(remaining.keys())  # Deterministic choice for efficiency
        allowed = remaining[a] - used  # Remove already used elements

        # Try each possible mapping for this element
        for b in allowed:
            # Extend current mapping
            current_mapping[a] = b
            new_used = used | {b}
            new_remaining = {x: vals for x, vals in remaining.items() if x != a}
            extend_mapping(current_mapping, new_remaining, new_used)
            del current_mapping[a]  # Backtrack

    # Start with fixed mappings and recursively extend
    extend_mapping(fixed_mappings.copy(), remaining_constraints, used_elements2)

    return candidate_mappings


def _is_homomorphism(
    algebra1: TransformationAlgebra,
    algebra2: TransformationAlgebra,
    mapping: dict[ActionType, ActionType],
) -> bool:
    """Check if a mapping is a homomorphism between the algebras.

    A mapping φ: A₁ → A₂ is a homomorphism if it preserves the algebraic structure:
    φ(x * y) = φ(x) * φ(y) for all x,y ∈ A₁

    Since we already know the mapping is bijective from _generate_candidate_mappings,
    if it's a homomorphism then it's also an isomorphism.

    Args:
        algebra1: First transformation algebra
        algebra2: Second transformation algebra
        mapping: Dict mapping elements of A₁ to elements of A₂

    Returns:
        True if mapping preserves algebraic structure, False otherwise
    """
    elements1 = algebra1.cayley_table_actions.get_row_labels()

    # Check φ(x * y) = φ(x) * φ(y) for all pairs x,y
    for x in elements1:
        for y in elements1:
            # Compute x * y in A₁ and map the result
            xy_in_a1 = algebra1.cayley_table_actions.compose_actions(
                left_action=x, right_action=y
            )
            mapped_result = mapping[xy_in_a1]

            # Compute φ(x) * φ(y) in A₂
            mapped_x = mapping[x]
            mapped_y = mapping[y]
            result_in_a2 = algebra2.cayley_table_actions.compose_actions(
                left_action=mapped_x, right_action=mapped_y
            )

            # Check if the results match
            if mapped_result != result_in_a2:
                return False

    return True


def _format_mapping(mapping: dict[ActionType, ActionType]) -> str:
    """Format an isomorphism mapping for display.

    Creates a string representation of the mapping φ: A₁ → A₂ showing
    how each element maps, sorted by the domain elements.

    Args:
        mapping: Dict representing the isomorphism

    Returns:
        Formatted string showing the mapping, e.g.:
        φ: A₁ → A₂
        a₁ ↦ x₂
        b₁ ↦ z₂
        c₁ ↦ y₂
    """
    # Sort domain elements for consistent display
    sorted_domain = sorted(mapping.keys())

    # Build mapping string with subscripts to indicate which algebra elements belong to
    lines = ["φ: A₁ → A₂"]
    lines.extend(f"{a}₁ ↦ {mapping[a]}₂" for a in sorted_domain)

    return "\n".join(lines)
