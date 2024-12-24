from itertools import product
from typing import NamedTuple, TypedDict

from utils.cayley_table_actions import CayleyTableActions
from utils.type_definitions import ActionType


class AssociativityViolation(NamedTuple):
    """Records a violation of associativity.

    Stores the triple (a,b,c) where (a ∘ b) ∘ c ≠ a ∘ (b ∘ c)
    along with the differing outcomes.
    """

    a: ActionType
    b: ActionType
    c: ActionType
    lhs_outcome: ActionType  # Result of (a ∘ b) ∘ c
    rhs_outcome: ActionType  # Result of a ∘ (b ∘ c)


class AssociativityResultType(TypedDict):
    """Result of checking associativity in a transformation algebra."""

    is_associative_algebra: bool
    violations: list[AssociativityViolation]


def check_associativity(
    cayley_table_actions: CayleyTableActions,
) -> AssociativityResultType:
    """Check if a transformation algebra is associative.

    Tests the associativity condition (a ∘ b) ∘ c = a ∘ (b ∘ c) for all triples
    of actions (a,b,c).

    Args:
        cayley_table_actions: The Cayley table for action composition

    Returns:
        AssociativityResultType containing:
        - is_associative_algebra: bool indicating if algebra is associative
        - violations: list of AssociativityViolation tuples for any violations found
    """
    result: AssociativityResultType = {"is_associative_algebra": True, "violations": []}

    actions = cayley_table_actions.get_row_labels()

    # Test all possible triples (a, b, c)
    for a, b, c in product(actions, repeat=3):
        # Calculate (a ∘ b) ∘ c
        ab = cayley_table_actions.compose_actions(a, b)
        lhs_outcome = cayley_table_actions.compose_actions(ab, c)

        # Calculate a ∘ (b ∘ c)
        bc = cayley_table_actions.compose_actions(b, c)
        rhs_outcome = cayley_table_actions.compose_actions(a, bc)

        # Check if associativity holds for this triple
        if lhs_outcome != rhs_outcome:
            result["is_associative_algebra"] = False
            result["violations"].append(
                AssociativityViolation(
                    a=a,
                    b=b,
                    c=c,
                    lhs_outcome=lhs_outcome,
                    rhs_outcome=rhs_outcome,
                )
            )

    return result
