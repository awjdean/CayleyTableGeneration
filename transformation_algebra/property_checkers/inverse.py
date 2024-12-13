from typing import NamedTuple, TypedDict

from cayley_tables.tables.cayley_table_actions import CayleyTableActions
from transformation_algebra.property_checkers.identity import IdentityResultType
from utils.type_definitions import ActionType


class InversePair(NamedTuple):
    """A pair of an inverse element and its corresponding identity."""

    inverse: ActionType
    identity: ActionType


class InverseResultsType(TypedDict):
    """Maps elements to their inverse-identity pairs."""

    left_inverses: dict[ActionType, list[InversePair]]
    right_inverses: dict[ActionType, list[InversePair]]
    inverses: dict[ActionType, list[InversePair]]
    is_inverse_algebra: bool


def check_inverse(
    cayley_table_actions: CayleyTableActions,
    identity_info: IdentityResultType | None,  # Allow None
) -> InverseResultsType:
    """Check if a transformation algebra has inverse elements.

    For an element a:
    - b is a left inverse if b ∘ a = e for some right identity e
    - b is a right inverse if a ∘ b = e for some left identity e
    - b is a two-sided inverse if it is both left and right inverse with same e

    Args:
        cayley_table_actions: The Cayley table for action composition
        identity_info: Result from checking identities, containing left/right identities

    Returns:
        InverseMapping containing:
        - left_inverses: Dict mapping elements to their left inverse-identity pairs
        - right_inverses: Dict mapping elements to their right inverse-identity pairs
        - inverses: Dict mapping elements to their two-sided inverse-identity pairs
        - is_inverse_algebra: True if every element has a two-sided inverse

    Raises:
        ValueError: If an element has different identities for left/right inverses
    """
    if identity_info is None:
        raise ValueError("Identity info must be computed before checking inverses")

    # Find left and right inverses
    left_inverses = _find_left_inverses(
        cayley_table_actions, identity_info["right_identities"]
    )
    right_inverses = _find_right_inverses(
        cayley_table_actions, identity_info["left_identities"]
    )

    # Find two-sided inverses
    inverses = _find_inverses(left_inverses, right_inverses)

    # Check if every element has an inverse
    all_actions = set(cayley_table_actions.get_row_labels())
    has_all_inverses = all(a in inverses for a in all_actions)

    return {
        "left_inverses": left_inverses,
        "right_inverses": right_inverses,
        "inverses": inverses,
        "is_inverse_algebra": has_all_inverses,
    }


def _find_left_inverses(
    cayley_table_actions: CayleyTableActions, right_identities: list[ActionType]
) -> dict[ActionType, list[InversePair]]:
    """Find all left inverses for each element.

    For element a, b is a left inverse if b ∘ a = e for some right identity e.

    Args:
        cayley_table_actions: The Cayley table for action composition
        right_identities: List of right identity elements

    Returns:
        Dict mapping each element to its list of (inverse, identity) pairs
    """
    left_inverses: dict[ActionType, list[InversePair]] = {}
    actions = cayley_table_actions.get_row_labels()

    # For each element a, find all its left inverses b where b ∘ a = e_r
    for a in actions:
        for b in actions:
            # Calculate b ∘ a
            outcome = cayley_table_actions.compose_actions(
                left_action=b, right_action=a
            )

            # Check if outcome is a right identity e_r
            if outcome in right_identities:
                if a not in left_inverses:
                    left_inverses[a] = []
                left_inverses[a].append(InversePair(inverse=b, identity=outcome))

    return left_inverses


def _find_right_inverses(
    cayley_table_actions: CayleyTableActions, left_identities: list[ActionType]
) -> dict[ActionType, list[InversePair]]:
    """Find all right inverses for each element.

    For element a, b is a right inverse if a ∘ b = e for some left identity e.

    Args:
        cayley_table_actions: The Cayley table for action composition
        left_identities: List of left identity elements

    Returns:
        Dict mapping each element to its list of (inverse, identity) pairs
    """
    right_inverses: dict[ActionType, list[InversePair]] = {}
    actions = cayley_table_actions.get_row_labels()

    # For each element a, find all its right inverses b where a ∘ b = e_l
    for a in actions:
        for b in actions:
            # Calculate a ∘ b
            outcome = cayley_table_actions.compose_actions(
                left_action=a, right_action=b
            )

            # Check if outcome is a left identity e_l
            if outcome in left_identities:
                if a not in right_inverses:
                    right_inverses[a] = []
                right_inverses[a].append(InversePair(inverse=b, identity=outcome))

    return right_inverses


def _find_inverses(
    left_inverses: dict[ActionType, list[InversePair]],
    right_inverses: dict[ActionType, list[InversePair]],
) -> dict[ActionType, list[InversePair]]:
    """Find all two-sided inverses.

    An element b is a two-sided inverse of a if:
    1. b is both a left and right inverse of a
    2. The identity element is the same in both cases

    Args:
        left_inverses: Dict mapping elements to their left inverse pairs
        right_inverses: Dict mapping elements to their right inverse pairs

    Returns:
        Dict mapping elements to their two-sided inverse pairs

    Raises:
        ValueError: If an element has different identities for left/right inverses
    """
    inverses: dict[ActionType, list[InversePair]] = {}

    # Check all elements that have both left and right inverses
    for a in set(left_inverses) & set(right_inverses):
        # Find pairs where same element is both left and right inverse
        for left_pair in left_inverses[a]:
            for right_pair in right_inverses[a]:
                if left_pair.inverse == right_pair.inverse:
                    # Check identities match
                    if left_pair.identity != right_pair.identity:
                        raise ValueError(
                            f"Element '{a}' has inverse '{left_pair.inverse}' with "
                            f"different identities: left={left_pair.identity}, "
                            f"right={right_pair.identity}"
                        )

                    if a not in inverses:
                        inverses[a] = []
                    inverses[a].append(left_pair)

    return inverses
