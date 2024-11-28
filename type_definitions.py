from typing import Any, TypedDict

# Worlds.
ActionType = str
MinActionsType = list[str]
StateType = tuple[Any, ...]
TransformationMatrix = dict[Any, dict[Any, Any]]  # TODO: fix types.

# Cayley table generation.
CayleyTableStatesDataType = dict[str, dict[str, StateType]]
CayleyTableActionsType = dict[str, dict[str, str]]


# Equivalence classes.
class EquivalenceClassEntryType(TypedDict):
    elements: set[ActionType]
    outcome: StateType


EquivalenceClassesDataType = dict[ActionType, EquivalenceClassEntryType]
