"""
Features present in any world class.
"""

from abc import abstractmethod

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.lines import Line2D

from utils.type_definitions import (
    ActionType,
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
        """
        Draw a visualization of the world's state space and transitions.
        Shows states as nodes and minimum actions as labeled edges.

        Args:
            include_undefined_state: If True, show undefined state and its transitions
            save_path: If provided, save the figure to this path
            show_edge_labels: If True, show labels on arrows
        """
        undefined_state = UndefinedStates.BASIC.value

        # Create a directed graph
        graph = nx.DiGraph()

        # Add nodes (states)
        for state in self.get_possible_states():
            if state != undefined_state or include_undefined_state:
                graph.add_node(state)

        # Add edges based on min_action_transformation_matrix
        edge_counts = {}  # Track number of edges between each node pair
        bidirectional_pairs = set()  # Track node pairs with edges in both directions

        # First pass: count edges and identify bidirectional pairs
        for state, actions in self._min_action_transformation_matrix.items():
            if (
                state != undefined_state or include_undefined_state
            ):  # Check source state
                for action, next_state in actions.items():
                    if (
                        next_state != undefined_state or include_undefined_state
                    ) and next_state is not None:
                        # Skip self-loops on undefined state
                        if state == next_state == undefined_state:
                            continue

                        # Create directional edge key (from_state, to_state)
                        edge_key = (state, next_state)
                        reverse_key = (next_state, state)

                        if reverse_key in edge_counts:
                            # Use tuple order based on string representation to ensure
                            #  consistency
                            bidirectional_pairs.add(
                                (state, next_state)
                                if str(state) <= str(next_state)
                                else (next_state, state)
                            )

                        edge_counts[edge_key] = edge_counts.get(edge_key, 0) + 1

        # Second pass: add edges with appropriate curvature
        for state, actions in self._min_action_transformation_matrix.items():
            if (
                state != undefined_state or include_undefined_state
            ):  # Check source state
                for action, next_state in actions.items():
                    if (
                        next_state != undefined_state or include_undefined_state
                    ) and next_state is not None:
                        # Skip self-loops on undefined state
                        if state == next_state == undefined_state:
                            continue

                        edge_key = (state, next_state)

                        # Calculate curvature without sorting
                        if state == next_state:
                            # Smaller curve for self-loops
                            rad = 0.2
                        elif (state, next_state) in bidirectional_pairs or (
                            next_state,
                            state,
                        ) in bidirectional_pairs:
                            # For bidirectional edges, curve one way or the other
                            rad = 0.3 if str(state) <= str(next_state) else -0.3
                        else:
                            # For one-way edges
                            rad = 0.0

                        graph.add_edge(
                            state,
                            next_state,
                            action=f"${action}$",
                            connectionstyle=f"arc3,rad={rad}",
                        )

        # Create the plot
        plt.figure(figsize=(10, 8))

        # Position nodes using spring layout with more spread
        pos = nx.spring_layout(
            graph, k=2, iterations=50
        )  # k controls spacing, higher = more spread

        # Create state labels mapping
        state_labels = {}
        sorted_states = sorted(graph.nodes(), key=str)
        for i, state in enumerate(sorted_states):
            if state == undefined_state:
                state_labels[state] = r"$\bot$"  # Use ⊥ for undefined state
            else:
                state_labels[state] = f"$w_{{{i}}}$"

        # Draw nodes with no transparency
        nx.draw_networkx_nodes(
            graph, pos, node_color="lightblue", node_size=1000, alpha=1.0
        )

        # Draw node labels
        nx.draw_networkx_labels(graph, pos, state_labels)

        # Create a color map for different actions
        unique_actions = set(
            action.strip("$")
            for action in nx.get_edge_attributes(graph, "action").values()
        )
        color_map = dict(
            zip(
                unique_actions,
                plt.get_cmap("Set3")(np.linspace(0, 1, len(unique_actions))),
            )
        )

        # Create action legend handles
        action_elements = [
            Line2D([0], [0], color=color_map[action], lw=2, label=f"${action}$")
            for action in sorted(unique_actions)
        ]

        # Create state legend handles
        state_elements = [
            Line2D([], [], color="none", label=f"{state_labels[state]} = {state}")
            for state in sorted(graph.nodes(), key=str)
        ]

        # Add combined legend
        plt.legend(
            handles=action_elements + state_elements,
            labels=[h.get_label() for h in action_elements + state_elements],
            title="Actions and States",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            title_fontsize=10,
            framealpha=1,
        )

        # Track processed edges to avoid drawing duplicates
        processed_edges = set()

        # Draw edges with arrows that start/end at node boundaries
        for edge in graph.edges():
            if edge in processed_edges:
                continue

            action = graph.edges[edge]["action"].strip("$")
            reverse_edge = (edge[1], edge[0])

            # Check if there's a reverse edge with the same action
            is_bidirectional = (
                reverse_edge in graph.edges()
                and graph.edges[reverse_edge]["action"].strip("$") == action
            )

            # Adjust curvature for self-loops
            if edge[0] == edge[1]:
                # Get all self-loop actions for this node
                self_loop_actions = sorted(
                    [
                        graph.edges[e]["action"].strip("$")
                        for e in graph.edges()
                        if e[0] == edge[0]
                        and e[0] == e[1]
                        and not (
                            e[0] == e[1] == undefined_state
                        )  # Skip undefined self-loops
                    ]
                )
                # Get index of current action in sorted actions
                action_index = self_loop_actions.index(action)

                # Use large fixed positions
                fixed_positions = [1.0, 2.0, 3.0, 4.0, 5.0]  # Add more if needed
                rad = fixed_positions[action_index]

                connectionstyle = f"arc3,rad={rad}"
            else:
                connectionstyle = graph.edges[edge]["connectionstyle"]

            if is_bidirectional:
                nx.draw_networkx_edges(
                    graph,
                    pos,
                    edgelist=[edge],
                    edge_color=color_map[action],
                    arrowsize=20,
                    arrows=True,
                    node_size=1000,
                    min_source_margin=20,
                    min_target_margin=20,
                    connectionstyle=connectionstyle,
                    arrowstyle="-|>" if edge[0] == edge[1] else "<|-|>",
                )
                processed_edges.add(edge)
                processed_edges.add(reverse_edge)
            else:
                # Draw single-headed arrow
                nx.draw_networkx_edges(
                    graph,
                    pos,
                    edgelist=[edge],
                    edge_color=color_map[action],
                    arrowsize=20,
                    arrows=True,
                    node_size=1000,
                    min_source_margin=20,
                    min_target_margin=20,
                    connectionstyle=connectionstyle,
                )

        # Draw edge labels centered on the curved arrows only if requested
        if show_edge_labels:
            edge_labels = {}
            processed_label_edges = set()

            for edge in graph.edges():
                if edge in processed_label_edges:
                    continue

                action = graph.edges[edge]["action"]
                reverse_edge = (edge[1], edge[0])

                # Check if there's a reverse edge with the same action
                is_bidirectional = (
                    reverse_edge in graph.edges()
                    and graph.edges[reverse_edge]["action"] == action
                )

                if is_bidirectional:
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

        plt.title(f"{self.__class__.__name__} State Transitions")
        plt.axis("off")
        plt.tight_layout()

        # Save the plot if a path is provided
        if save_path is not None:
            plt.savefig(
                save_path,
                format="png",
                bbox_inches="tight",
                dpi=300,
            )

        # Show the plot
        plt.show()
