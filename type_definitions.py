from typing import Any, TypedDict

# Worlds.
ActionType = str
MinActionsType = list[str]
StateType = tuple[Any, ...]
TransformationMatrix = dict[Any, dict[Any, Any]]  # TODO: fix types.

# Cayley table generation.
CayleyTableStatesRowType = dict[ActionType, StateType]
CayleyTableStatesDataType = dict[ActionType, CayleyTableStatesRowType]
CayleyTableActionsType = dict[ActionType, dict[ActionType, ActionType]]


# Equivalence classes.
class EquivalenceClassEntryType(TypedDict):
    elements: set[ActionType]
    outcome: StateType


EquivalenceClassesDataType = dict[ActionType, EquivalenceClassEntryType]


class EquivElementsRowColumnDictType(TypedDict):
    row: CayleyTableStatesRowType
    column: CayleyTableStatesRowType
