"""
Features present in any world class.
"""

from abc import abstractmethod
from itertools import zip_longest

import pygraphviz as pgv

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
        show_legend: bool = True,
        dpi: int = 300,
    ) -> None:
        """Draw a visualization of the world's state space and transitions."""
        import tempfile
        import webbrowser
        from pathlib import Path

        graph = self._create_and_layout_graph(
            include_undefined_state, show_edge_labels, show_legend
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            graph.draw(tmp.name, format="png", args=f"-Gdpi={dpi}")
            output_path = Path(save_path if save_path else tmp.name)

            if save_path:
                Path(tmp.name).rename(output_path)

            webbrowser.open(f"file://{output_path.absolute()}")

    def _create_and_layout_graph(
        self,
        include_undefined_state: bool,
        show_edge_labels: bool = False,
        show_legend: bool = True,
    ) -> pgv.AGraph:
        """Create and layout the graph."""
        graph = pgv.AGraph(
            directed=True,
            strict=False,
            overlap="false",
            splines="spline",
            concentrate="false",
            rankdir="LR",
            label=self._create_legend_label() if show_legend else "",
            labelloc="t",
            labeljust="r",
            fontname="Computer Modern Math",
            start="random",
        )

        # Set default node and edge attributes
        graph.node_attr.update(
            shape="circle",
            style="filled",
            fillcolor="lightblue",
            width="0.75",
            fontname="Computer Modern Math",
            fontsize="18",
            margin="0.2",
            layer="back",  # Put nodes in back layer
        )
        graph.edge_attr.update(
            fontsize="10",
            arrowsize="0.8",
            fontname="Computer Modern Math",
            penwidth="1.5",
            weight="1.0",
            layer="front",  # Put edges in front layer
        )

        self._add_nodes_and_edges(graph, include_undefined_state, show_edge_labels)
        graph.layout(prog="neato")
        return graph

    def _create_color_map(self) -> dict[str, str]:
        """Create a color map for actions."""
        colors = [
            "#1f77b4",  # Steel blue
            "#d62728",  # Crimson
            "#2ca02c",  # Forest green
            "#9467bd",  # Medium purple
            "#ff7f0e",  # Dark orange
            "#17becf",  # Light blue
            "#e377c2",  # Pink
            "#8c564b",  # Brown
            "#7f7f7f",  # Gray
            "#bcbd22",  # Olive
        ]
        return {
            action: colors[i % len(colors)]
            for i, action in enumerate(sorted(self._MIN_ACTIONS))
        }

    def _create_legend_label(self) -> str:
        """Create HTML-like label for the legend."""
        color_map = self._create_color_map()
        undefined_state = UndefinedStates.BASIC.value

        # Build legend table with two columns
        legend = ['<<TABLE BORDER="0" CELLBORDER="0">']
        legend.append("<TR><TD>Actions</TD><TD>States</TD></TR>")

        # Get states ready
        states = self.get_possible_states()
        nodes = sorted((s for s in states if s != undefined_state), key=str)
        if undefined_state in states:
            nodes.append(undefined_state)

        # Create subscript translator
        subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

        # Add actions and states side by side
        for i, (action_pair, state) in enumerate(
            zip_longest(sorted(color_map.items()), nodes, fillvalue=(None, None))
        ):
            # Create action cell
            action_cell = (
                f'<TD><FONT COLOR="{action_pair[1]}">{action_pair[0]} →</FONT></TD>'
                if action_pair[0] is not None
                else "<TD></TD>"
            )

            # Create state cell
            if state is not None:
                if state == undefined_state:
                    label = "⊥"
                else:
                    subscript = str(i).translate(subscripts)
                    label = f"w{subscript}"
                state_cell = f"<TD>{label} = {state}</TD>"
            else:
                state_cell = "<TD></TD>"

            # Add row
            legend.append(f"<TR>{action_cell}{state_cell}</TR>")

        legend.append("</TABLE>>")
        return "".join(legend)

    def _add_nodes_and_edges(
        self, graph: pgv.AGraph, include_undefined_state: bool, show_edge_labels: bool
    ) -> None:
        """Add nodes and edges to the graph."""
        # Unicode subscript digits mapping
        subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

        undefined_state = UndefinedStates.BASIC.value
        color_map = self._create_color_map()

        # Track self-loops per node to position them
        self_loop_counts = {}

        # Port positions with angles
        port_configs = [
            ("n", "0"),  # North at 0°
            ("ne", "45"),  # Northeast at 45°
            ("e", "0"),  # East at 0°
            ("se", "-45"),  # Southeast at -45°
            ("s", "0"),  # South at 0°
            ("sw", "-45"),  # Southwest at -45°
            ("w", "0"),  # West at 0°
            ("nw", "45"),  # Northwest at 45°
        ]

        # Add nodes with labels
        states = self.get_possible_states()
        nodes = sorted((s for s in states if s != undefined_state), key=str)
        if include_undefined_state:
            nodes.append(undefined_state)

        # Add regular state nodes
        for i, state in enumerate(nodes):
            if state == undefined_state:
                graph.add_node(state, label="⊥")
            else:
                # Convert number to subscript
                subscript = str(i).translate(subscripts)
                graph.add_node(state, label=f"w{subscript}")

        # Add edges
        for state, actions in self._min_action_transformation_matrix.items():
            if state != undefined_state or include_undefined_state:
                for action, next_state in actions.items():
                    if next_state != undefined_state or include_undefined_state:
                        if state == next_state == undefined_state:
                            continue

                        edge_color = color_map[action]
                        edge_attrs = {
                            "color": edge_color,
                            "fontcolor": edge_color,
                        }
                        if show_edge_labels:
                            edge_attrs["label"] = action

                        if state == next_state:
                            # Count self-loops for this node
                            self_loop_counts[state] = self_loop_counts.get(state, 0) + 1
                            count = self_loop_counts[state]

                            # Get port and angle
                            port, angle = port_configs[count % len(port_configs)]

                            edge_attrs.update(
                                {
                                    "dir": "both",
                                    "arrowhead": "normal",
                                    "arrowtail": "none",
                                    "headport": port,
                                    "tailport": port,
                                    "headclip": "false",
                                    "tailclip": "false",
                                    "labelangle": angle,
                                    "len": "1.0",
                                    "weight": "0.1",
                                    "constraint": "false",
                                }
                            )
                        else:
                            edge_attrs.update(
                                {
                                    "dir": "forward",
                                    "arrowhead": "normal",
                                }
                            )

                        graph.add_edge(state, next_state, **edge_attrs)

    def _add_edge(
        self,
        graph: pgv.AGraph,
        source: StateType,
        target: StateType,
        action: str,
        color: str,
    ) -> None:
        """Add a single edge to the graph."""
        edge_attrs = {
            "label": action,
            "color": color,
            "fontcolor": color,
            "dir": "both" if source == target else "forward",
            "arrowhead": "normal",
            "arrowtail": "none" if source == target else None,
        }
        graph.add_edge(source, target, **edge_attrs)

    def _add_node(
        self,
        graph: pgv.AGraph,
        state: StateType,
        index: int,
        subscripts: dict[int, int],
    ) -> None:
        """Add a single node to the graph."""
        is_undefined = state == UndefinedStates.BASIC.value
        label = "⊥" if is_undefined else f"w{str(index).translate(subscripts)}"
        graph.add_node(state, label=label)
