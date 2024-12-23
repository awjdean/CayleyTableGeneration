from enum import Enum
from typing import Any, TypedDict

# Base world.
ActionType = str
MinActionsType = list[ActionType]
StateType = tuple[Any, ...]
TransformationMatrix = dict[StateType, dict[ActionType, StateType]]

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


# Gridworlds2d.
GridPosition2DType = tuple[int, int]


class AlgebraGenerationMethod(str, Enum):
    STATES_CAYLEY = "states_cayley"
    ACTION_FUNCTION = "action_function"
    LOCAL_ACTION_FUNCTION = "local_action_function"
