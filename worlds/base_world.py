"""
Features present in any world class.
"""

from abc import abstractmethod

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

from utils.type_definitions import (
    ActionType,
    EdgeDrawingParams,
    MinActionsType,
    StateType,
    TransformationMatrix,
)
from worlds.utils.undefined_state import UndefinedStates
from worlds.world_saver import WorldSaver


class BaseWorld:
    def __init__(self, min_actions) -> None:
        self._current_state: StateType
        self._MIN_ACTIONS: list[ActionType] = min_actions
        self._min_action_transformation_matrix: TransformationMatrix = {}
        self._possible_states: list[StateType] = []
        self.world_saver = WorldSaver()

    @abstractmethod
    def generate_possible_states(self) -> list[StateType]:
        """Return a list of possible states for the world."""
        raise NotImplementedError("Subclasses must implement generate_possible_states.")

    @abstractmethod
    def get_next_state(self, state: StateType, min_action: ActionType) -> StateType:
        """Return the next state given the current state and a minimum action."""
        raise NotImplementedError("Subclasses must implement get_next_state.")

    def get_state(self) -> StateType:
        return self._current_state

    def set_state(self, state: StateType) -> None:
        """Set the current state of the world.

        Args:
            state (StateType): The state to set as the current state.

        Raises:
            ValueError: If the state is not in the list of possible states.
        """
        possible_states = self.get_possible_states()
        if state not in possible_states:
            raise ValueError(
                f"Invalid state: {state}. " f"State must be one of {possible_states}."
            )
        self._current_state = state

    def get_possible_states(self) -> list[StateType]:
        if not self._possible_states:
            print("\tGenerating possible states.")
            self._possible_states = self.generate_possible_states()
        return self._possible_states

    def generate_min_action_transformation_matrix(self) -> None:
        """Generate the transformation matrix for all possible state-action pairs.

        Raises:
            ValueError: If possible states or minimum actions are not defined.
        """
        if self._min_action_transformation_matrix:
            print("Transformation matrix already exists.")
        elif not self._MIN_ACTIONS:
            raise ValueError("Minimum actions are not defined.")
        else:
            self._add_undefined_state_to_possible_states()
            transformation_matrix: TransformationMatrix = {}
            for state in self.get_possible_states():
                transformation_matrix[state] = {}
                for min_action in self._MIN_ACTIONS:
                    # Undefined state is absorbing.
                    if state == UndefinedStates.BASIC.value:
                        next_state = UndefinedStates.BASIC.value
                    else:
                        next_state = self.get_next_state(state, min_action)
                    transformation_matrix[state][min_action] = next_state
            self._min_action_transformation_matrix = transformation_matrix

    def _add_undefined_state_to_possible_states(self) -> None:
        """
        Add the undefined state to the list of possible states if it is not already
         present.
        """
        undefined_state = UndefinedStates.BASIC.value
        if undefined_state not in self.get_possible_states():
            self._possible_states.append(undefined_state)

    def _apply_min_action(self, min_action: ActionType) -> None:
        """Lookup a precomputed state-action pair in the transformation matrix.

        Args:
            min_action (ActionType): The minimum action to apply.

        Raises:
            ValueError: If the minimum action transformation matrix is not defined or if
            the state-action pair is invalid.
        """
        if self._min_action_transformation_matrix is None:
            raise ValueError("Minimum action transformation matrix is not defined.")

        if self._current_state not in self._min_action_transformation_matrix:
            raise ValueError(
                f"Current state {self._current_state} is not valid in the"
                " transformation matrix."
            )

        try:
            self._current_state = self._min_action_transformation_matrix[
                self._current_state
            ][min_action]
        except KeyError:
            raise ValueError(
                f"Invalid state-action pair: {self._current_state}-{min_action}. "
                f"Check if the action is valid for the current state."
            )

    def apply_action_sequence(self, action_sequence: ActionType) -> None:
        """Apply a sequence of actions in reverse order.

        Args:
            action_sequence (ActionType): The sequence of actions to apply.

        # TODO: Build in a check here so that if action goes to the undefined state, we
        #  can skip the rest of the lookups.
        """
        for min_action in action_sequence[::-1]:
            self._apply_min_action(min_action)

    def get_min_actions(self) -> MinActionsType:
        return self._MIN_ACTIONS

    def save_world_properties(self, path: str) -> None:
        """Save the world properties to a JSON file."""
        properties = self._get_world_properties_for_save()
        self.world_saver.save_world_properties(properties, path)

    def load_world_properties(self, path: str) -> None:
        """Load the world properties from a pickle file."""
        # Get the keys of additional properties that need to be loaded
        additional_properties_keys = set(
            self._get_additional_properties_for_save().keys()
        )

        # Load properties using WorldSaver
        properties = self.world_saver.load_world_properties(
            path, additional_properties_keys
        )

        # Set the properties
        self._MIN_ACTIONS = properties["minimum_actions"]
        self._possible_states = properties["possible_states"]
        self._min_action_transformation_matrix = properties[
            "min_action_transformation_matrix"
        ]

        # Set additional properties
        for key, value in properties.items():
            if key not in [
                "minimum_actions",
                "possible_states",
                "min_action_transformation_matrix",
            ]:
                setattr(self, f"_{key.upper()}", value)

    def _get_world_properties_for_save(self) -> dict:
        """Collect all relevant world properties into a dictionary.

        Returns:
            dict: Dictionary containing world properties including minimum actions,
                 possible states, and transformation matrix.
        """
        return {
            "minimum_actions": self._MIN_ACTIONS,
            "possible_states": self._possible_states,
            "min_action_transformation_matrix": self._min_action_transformation_matrix,
            **self._get_additional_properties_for_save(),
        }

    def _get_additional_properties_for_save(self) -> dict:
        """Get additional properties specific to the world subclass.

        Returns:
            dict: Additional properties to save. Empty by default.
        """
        return {}

    def draw_graph(
        self,
        include_undefined_state: bool = False,
        save_path: str | None = None,
        show_edge_labels: bool = False,
    ) -> None:
        """Draw a visualization of the world's state space and transitions."""
        graph = self._create_graph(include_undefined_state)
        pos = self._setup_graph_layout(graph)
        state_labels = self._create_state_labels(graph)

        plt.figure(figsize=(10, 8))
        self._draw_nodes_and_labels(graph, pos, state_labels)

        color_map = self._create_color_map(graph)
        self._draw_edges(graph, pos, color_map)

        if show_edge_labels:
            self._draw_edge_labels(graph, pos)

        self._add_legend(graph, state_labels, color_map)
        self._finalize_plot(save_path)

    def _create_graph(self, include_undefined_state: bool) -> nx.DiGraph:
        """Create directed graph with nodes and edges."""
        graph = nx.DiGraph()
        undefined_state = UndefinedStates.BASIC.value

        # Add nodes
        for state in self.get_possible_states():
            if state != undefined_state or include_undefined_state:
                graph.add_node(state)

        # Add edges with curvature
        bidirectional_pairs = self._identify_bidirectional_pairs(
            include_undefined_state
        )

        for state, actions in self._min_action_transformation_matrix.items():
            if state != undefined_state or include_undefined_state:
                self._add_edges_for_state(
                    graph, state, actions, bidirectional_pairs, include_undefined_state
                )

        return graph

    def _identify_bidirectional_pairs(self, include_undefined_state: bool) -> set:
        """Identify pairs of states with bidirectional edges."""
        undefined_state = UndefinedStates.BASIC.value
        bidirectional_pairs = set()
        edge_counts = {}

        for state, actions in self._min_action_transformation_matrix.items():
            if state != undefined_state or include_undefined_state:
                for action, next_state in actions.items():
                    if next_state != undefined_state or include_undefined_state:
                        if state == next_state == undefined_state:
                            continue
                        edge_key = (state, next_state)
                        reverse_key = (next_state, state)
                        if reverse_key in edge_counts:
                            ordered_pair = (
                                (state, next_state)
                                if str(state) <= str(next_state)
                                else (next_state, state)
                            )
                            bidirectional_pairs.add(ordered_pair)
                        edge_counts[edge_key] = edge_counts.get(edge_key, 0) + 1

        return bidirectional_pairs

    def _add_edges_for_state(
        self,
        graph: nx.DiGraph,
        state: StateType,
        actions: dict,
        bidirectional_pairs: set,
        include_undefined_state: bool,
    ) -> None:
        """Add edges for a given state to the graph."""
        undefined_state = UndefinedStates.BASIC.value

        for action, next_state in actions.items():
            if next_state != undefined_state or include_undefined_state:
                if state == next_state == undefined_state:
                    continue

                rad = self._calculate_edge_curvature(
                    state, next_state, bidirectional_pairs
                )
                graph.add_edge(
                    state,
                    next_state,
                    action=f"${action}$",
                    connectionstyle=f"arc3,rad={rad}",
                )

    def _calculate_edge_curvature(
        self,
        state: StateType,
        next_state: StateType,
        bidirectional_pairs: set,
    ) -> float:
        """Calculate the curvature for an edge."""
        if state == next_state:
            return 0.2  # Smaller curve for self-loops
        elif (state, next_state) in bidirectional_pairs or (
            next_state,
            state,
        ) in bidirectional_pairs:
            return 0.3 if str(state) <= str(next_state) else -0.3
        return 0.0  # For one-way edges

    def _setup_graph_layout(
        self, graph: nx.DiGraph
    ) -> dict[StateType, tuple[float, float]]:
        """Create the graph layout."""
        return dict(nx.spring_layout(graph, k=2, iterations=50))

    def _create_state_labels(self, graph: nx.DiGraph) -> dict:
        """Create labels for states in the graph."""
        state_labels = {}
        undefined_state = UndefinedStates.BASIC.value

        for i, state in enumerate(sorted(graph.nodes(), key=str)):
            if state == undefined_state:
                state_labels[state] = r"$\bot$"  # Use ⊥ for undefined state
            else:
                state_labels[state] = f"$w_{{{i}}}$"

        return state_labels

    def _draw_nodes_and_labels(
        self, graph: nx.DiGraph, pos: dict, state_labels: dict
    ) -> None:
        """Draw nodes and their labels."""
        nx.draw_networkx_nodes(
            graph, pos, node_color="lightblue", node_size=1000, alpha=1.0
        )
        nx.draw_networkx_labels(graph, pos, state_labels)

    def _create_color_map(self, graph: nx.DiGraph) -> dict:
        """Create a color map for different actions."""
        unique_actions = set(
            action.strip("$")
            for action in nx.get_edge_attributes(graph, "action").values()
        )
        return {action: f"C{i}" for i, action in enumerate(sorted(unique_actions))}

    def _draw_edges(self, graph: nx.DiGraph, pos: dict, color_map: dict) -> None:
        """Draw edges with proper styling."""
        processed_edges = set()

        for edge in graph.edges():
            if edge in processed_edges:
                continue

            action = graph.edges[edge]["action"].strip("$")
            reverse_edge = (edge[1], edge[0])
            is_bidirectional = (
                reverse_edge in graph.edges()
                and graph.edges[reverse_edge]["action"].strip("$") == action
            )

            self._draw_single_edge(
                {
                    "graph": graph,
                    "pos": pos,
                    "edge": edge,
                    "action": action,
                    "color": color_map[action],
                    "is_bidirectional": is_bidirectional,
                    "processed_edges": processed_edges,
                }
            )

    def _draw_single_edge(self, params: EdgeDrawingParams) -> None:
        """Draw a single edge with proper styling."""
        reverse_edge = (params["edge"][1], params["edge"][0])
        connectionstyle = params["graph"].edges[params["edge"]]["connectionstyle"]

        if params["is_bidirectional"]:
            nx.draw_networkx_edges(
                params["graph"],
                params["pos"],
                edgelist=[params["edge"]],
                edge_color=params["color"],
                arrowsize=20,
                arrows=True,
                node_size=1000,
                min_source_margin=20,
                min_target_margin=20,
                connectionstyle=connectionstyle,
                arrowstyle="<|-|>" if params["edge"][0] != params["edge"][1] else "-|>",
            )
            params["processed_edges"].add(params["edge"])
            params["processed_edges"].add(reverse_edge)
        else:
            nx.draw_networkx_edges(
                params["graph"],
                params["pos"],
                edgelist=[params["edge"]],
                edge_color=params["color"],
                arrowsize=20,
                arrows=True,
                node_size=1000,
                min_source_margin=20,
                min_target_margin=20,
                connectionstyle=connectionstyle,
            )

    def _draw_edge_labels(self, graph: nx.DiGraph, pos: dict) -> None:
        """Draw labels for edges."""
        edge_labels = {}
        processed_label_edges = set()

        for edge in graph.edges():
            if edge in processed_label_edges:
                continue

            action = graph.edges[edge]["action"]
            reverse_edge = (edge[1], edge[0])

            if (
                reverse_edge in graph.edges()
                and graph.edges[reverse_edge]["action"] == action
            ):
                processed_label_edges.add(edge)
                processed_label_edges.add(reverse_edge)

            edge_labels[edge] = action

        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels,
            label_pos=0.3,
            rotate=False,
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                alpha=0.8,
                pad=2.0,
            ),
            font_size=10,
        )

    def _add_legend(
        self, graph: nx.DiGraph, state_labels: dict, color_map: dict
    ) -> None:
        """Add legend showing actions and state mappings."""
        # Create legend entries for actions
        action_entries = [
            (action, color) for action, color in sorted(color_map.items())
        ]

        # Create legend entries for states
        state_entries = [
            (f"{state_labels[state]} = {state}", "none")
            for state in sorted(graph.nodes(), key=str)
        ]

        # Add legend using Line2D from matplotlib.lines
        plt.legend(
            handles=[
                Line2D([], [], color=color, label=f"${action}$")
                for action, color in action_entries
            ]
            + [
                Line2D([], [], color=color, label=label)
                for label, color in state_entries
            ],
            title="Actions and States",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            title_fontsize=10,
            framealpha=1,
        )

    def _finalize_plot(self, save_path: str | None) -> None:
        """Finalize and optionally save the plot."""
        plt.title(f"{self.__class__.__name__} State Transitions")
        plt.axis("off")
        plt.tight_layout()

        if save_path is not None:
            plt.savefig(
                save_path,
                format="png",
                bbox_inches="tight",
                dpi=300,
            )

        plt.show()
