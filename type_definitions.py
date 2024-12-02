from typing import Any, TypedDict

# Worlds.
ActionType = str
MinActionsType = list[str]
StateType = tuple[Any, ...]
TransformationMatrix = dict[Any, dict[Any, Any]]  # TODO: fix types.

# States Cayley table generation.
CayleyTableStatesRowType = dict[ActionType, StateType]
CayleyTableStatesDataType = dict[ActionType, CayleyTableStatesRowType]

# Actions Cayley table generation.
CayleyTableActionsRowType = dict[ActionType, ActionType]
CayleyTableActionsDataType = dict[ActionType, CayleyTableActionsRowType]


# Equivalence classes.
class EquivClassEntryType(TypedDict):
    elements: set[ActionType]
    outcome: StateType


EquivClassesDataType = dict[ActionType, EquivClassEntryType]


class EquivElementsRowColumnDictType(TypedDict):
    row: CayleyTableStatesRowType
    column: CayleyTableStatesRowType
