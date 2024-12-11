from math import inf
from typing import NamedTuple, TypedDict

from cayley_tables.cayley_table_actions import CayleyTableActions
from transformation_algebra.property_checkers.identity import IdentityResultType
from utils.type_definitions import ActionType


class OrderSearchCycle(NamedTuple):
    """Information about a cycle found during order search."""

    cycle_start: ActionType
    cycle_length: int


class ElementOrderInfo(NamedTuple):
    """Information about an element's order.

    Contains:
    - order: The order of the element (inf if infinite)
    - power_sequence: Sequence of powers [a, a², a³, ...]
    - cycle: Information about cycle if order is infinite
    """

    order: int | float
    power_sequence: list[ActionType]
    cycle: OrderSearchCycle | None = None


class ElementOrderResultType(TypedDict):
    """Maps elements to their order information."""

    orders: dict[ActionType, ElementOrderInfo]


def calculate_element_orders(
    cayley_table_actions: CayleyTableActions,
    identity_info: IdentityResultType | None,
) -> ElementOrderResultType:
    """Find the order of each element in a transformation algebra.

    The order of an element a is the smallest positive integer n such that
    a^n = e (where e is the identity element). If no such n exists, the
    element has infinite order.

    Args:
        cayley_table_actions: The Cayley table for action composition
        identity_info: Result from checking identities, containing identity elements

    Returns:
        ElementOrderResultType containing:
        orders: Dict mapping each element to its order information

    Raises:
        ValueError: If no identity element exists
    """
    if identity_info is None:
        raise ValueError("Identity info must be computed before calculating orders")

    identities = identity_info["identities"]
    if not identities:
        raise ValueError("Cannot calculate element orders: No identity element exists")

    # There should only be one identity element
    identity = identities[0]
    orders: dict[ActionType, ElementOrderInfo] = {}

    # TODO: check this.
    # Maximum possible finite order is |\hat{A}^{*}| (size of algebra)
    max_order = len(cayley_table_actions.get_row_labels())

    for element in cayley_table_actions.get_row_labels():
        orders[element] = _find_element_order(
            cayley_table_actions, element, identity, max_order
        )

    return {"orders": orders}


def _find_element_order(
    cayley_table_actions: CayleyTableActions,
    element: ActionType,
    identity: ActionType,
    max_order: int,
) -> ElementOrderInfo:
    """Find the order of a single element.

    Args:
        cayley_table_actions: The Cayley table for action composition
        element: The element to find the order of
        identity: The identity element
        max_order: Maximum possible finite order

    Returns:
        ElementOrderInfo containing order and power sequence information

    Raises:
        ValueError: If power sequence exceeds maximum order
    """
    # Identity element has order 1
    if element == identity:
        return ElementOrderInfo(order=1, power_sequence=[element])

    power_sequence = [element]
    current_power = element

    # Keep taking powers until we hit identity or find a cycle
    for n in range(2, max_order + 1):
        # Calculate next power: a^n = a * a^(n-1)
        current_power = cayley_table_actions.compose_actions(
            left_action=element, right_action=current_power
        )
        power_sequence.append(current_power)

        # Check if we've reached identity
        if current_power == identity:
            return ElementOrderInfo(order=n, power_sequence=power_sequence)

        # Check if we've found a cycle
        if current_power in power_sequence[:-1]:
            cycle_start = current_power
            cycle_length = power_sequence[:-1][::-1].index(current_power) + 1
            return ElementOrderInfo(
                order=inf,
                power_sequence=power_sequence,
                cycle=OrderSearchCycle(
                    cycle_start=cycle_start,
                    cycle_length=cycle_length,
                ),
            )

    raise ValueError(
        f"Power sequence for element '{element}' exceeded maximum order {max_order}"
    )
