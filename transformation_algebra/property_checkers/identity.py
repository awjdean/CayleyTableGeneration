from typing import TypedDict

from cayley_tables.cayley_table_actions import CayleyTableActions
from utils.type_definitions import ActionType


class IdentityResultType(TypedDict):
    """Result of checking for identity elements in a transformation algebra."""

    is_identity_algebra: bool
    left_identities: list[ActionType]
    right_identities: list[ActionType]
    identities: list[ActionType]


def check_identity(cayley_table_actions: CayleyTableActions) -> IdentityResultType:
    """
    Check if a transformation algebra has identity elements.

    An element e is:
    - A left identity if e ∘ a = a for all actions a
    - A right identity if a ∘ e = a for all actions a
    - A two-sided identity if it is both a left and a right identity

    Args:
        cayley_table_actions: The Cayley table for action composition

    Returns:
        IdentityResultType containing:
        - is_identity_algebra: True if exactly one two-sided identity exists
        - left_identities: List of all left identity elements
        - right_identities: List of all right identity elements
        - identities: List of all two-sided identity elements

    Raises:
        ValueError: If more than one two-sided identity is found
    """
    # Find left and right identities
    left_identities = _find_left_identities(cayley_table_actions)
    right_identities = _find_right_identities(cayley_table_actions)

    # Find two-sided identities
    identities = [e for e in left_identities if e in right_identities]

    if len(identities) > 1:
        raise ValueError(
            f"Invalid algebra: Found multiple identity elements: {sorted(identities)}"
        )

    return {
        "is_identity_algebra": len(identities) == 1,
        "left_identities": left_identities,
        "right_identities": right_identities,
        "identities": identities,
    }


def _find_left_identities(cayley_table_actions: CayleyTableActions) -> list[ActionType]:
    """Find all left identity elements.

    An element e is a left identity if e ∘ a = a for all actions a.
    """
    actions = cayley_table_actions.get_row_labels()
    left_identities = []

    # Test each potential left identity e_l
    for e_l in actions:
        is_left_identity = True
        # Must satisfy e_l ∘ a = a for all a
        for a in actions:
            if (
                cayley_table_actions.compose_actions(left_action=e_l, right_action=a)
                != a
            ):
                is_left_identity = False
                break
        if is_left_identity:
            left_identities.append(e_l)

    return left_identities


def _find_right_identities(
    cayley_table_actions: CayleyTableActions,
) -> list[ActionType]:
    """Find all right identity elements.

    An element e is a right identity if a ∘ e = a for all actions a.
    """
    actions = cayley_table_actions.get_row_labels()
    right_identities = []

    # Test each potential right identity e_r
    for e_r in actions:
        is_right_identity = True
        # Must satisfy a ∘ e_r = a for all a
        for a in actions:
            if (
                cayley_table_actions.compose_actions(left_action=a, right_action=e_r)
                != a
            ):
                is_right_identity = False
                break
        if is_right_identity:
            right_identities.append(e_r)

    return right_identities
