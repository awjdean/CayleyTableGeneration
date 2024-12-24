from typing import Any, TypedDict

import networkx as nx

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


class EdgeDrawingParams(TypedDict):
    graph: nx.DiGraph
    pos: dict
    edge: tuple
    action: str
    color: str
    is_bidirectional: bool
    processed_edges: set
