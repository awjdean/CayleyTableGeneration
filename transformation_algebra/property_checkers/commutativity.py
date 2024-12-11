from typing import TypedDict

from cayley_tables.cayley_table_actions import CayleyTableActions
from utils.type_definitions import ActionType


class CommutativityResultType(TypedDict):
    """Result of checking commutativity in a transformation algebra."""

    is_commutative_algebra: bool
    commuting_elements: dict[ActionType, list[ActionType]]
    non_commuting_elements: dict[ActionType, list[ActionType]]
    commute_with_all: list[ActionType]


def check_commutativity(
    cayley_table_actions: CayleyTableActions,
) -> CommutativityResultType:
    """Check if a transformation algebra is commutative.

    Two elements a,b commute if a ∘ b = b ∘ a.
    The algebra is commutative if all pairs of elements commute.

    Args:
        cayley_table_actions: The Cayley table for action composition

    Returns:
        CommutativityResultType containing:
        - is_commutative_algebra: True if all elements commute with each other
        - commuting_elements: Dict mapping each element to list of elements it commutes
          with
        - non_commuting_elements: Dict mapping each element to list of elements it
          doesn't commute with
        - commute_with_all: List of elements that commute with every other element
    """
    # Find commuting and non-commuting pairs
    commuting_elements, non_commuting_elements = _find_commuting_pairs(
        cayley_table_actions
    )

    # Find elements that commute with everything
    commute_with_all = _find_universal_commuters(
        cayley_table_actions, commuting_elements
    )

    # Algebra is commutative if every element commutes with all others
    all_actions = cayley_table_actions.get_row_labels()
    is_commutative = len(commute_with_all) == len(all_actions)

    return {
        "is_commutative_algebra": is_commutative,
        "commuting_elements": commuting_elements,
        "non_commuting_elements": non_commuting_elements,
        "commute_with_all": commute_with_all,
    }


def _find_commuting_pairs(
    cayley_table_actions: CayleyTableActions,
) -> tuple[dict[ActionType, list[ActionType]], dict[ActionType, list[ActionType]]]:
    """Find all pairs of elements that commute/don't commute.

    Args:
        cayley_table_actions: The Cayley table for action composition

    Returns:
        Tuple containing:
        - Dict mapping each element to list of elements it commutes with
        - Dict mapping each element to list of elements it doesn't commute with
    """
    commuting: dict[ActionType, list[ActionType]] = {}
    non_commuting: dict[ActionType, list[ActionType]] = {}
    actions = cayley_table_actions.get_row_labels()

    for a in actions:
        commuting[a] = []
        non_commuting[a] = []
        for b in actions:
            # Check if a ∘ b = b ∘ a
            a_b = cayley_table_actions.compose_actions(left_action=a, right_action=b)
            b_a = cayley_table_actions.compose_actions(left_action=b, right_action=a)

            if a_b == b_a:
                commuting[a].append(b)
            else:
                non_commuting[a].append(b)

    return commuting, non_commuting


def _find_universal_commuters(
    cayley_table_actions: CayleyTableActions,
    commuting_elements: dict[ActionType, list[ActionType]],
) -> list[ActionType]:
    """Find elements that commute with every other element.

    Args:
        cayley_table_actions: The Cayley table for action composition
        commuting_elements: Dict mapping elements to what they commute with

    Returns:
        List of elements that commute with every other element
    """
    all_actions = set(cayley_table_actions.get_row_labels())
    return [a for a in all_actions if set(commuting_elements[a]) == all_actions]
