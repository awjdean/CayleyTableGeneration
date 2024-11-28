from typing import Any, TypedDict

# Worlds.
ActionType = str
MinActionsType = list[str]
StateType = tuple[Any, ...]
TransformationMatrix = dict[Any, dict[Any, Any]]

# Cayley table generation.
CayleyTableStatesType = dict[str, dict[str, Any]]
CayleyTableActionsType = dict[str, dict[str, str]]


# Equivalence classes.
class EquivalenceClassEntryType(TypedDict):
    elements: set[str]
    outcome: StateType


EquivalenceClassesType = dict[str, EquivalenceClassEntryType]
