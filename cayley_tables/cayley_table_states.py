import pandas as pd

from cayley_tables.action_outcome import (
    generate_action_outcome,
)
from cayley_tables.equiv_classes import EquivClasses
from utils.type_definitions import (
    ActionType,
    CayleyTableStatesDataType,
    CayleyTableStatesRowType,
    EquivElementsRowColumnDictType,
    StateType,
)
from worlds.base_world import BaseWorld


class CayleyTableStates:
    """
    Represents a Cayley table mapping action compositions to their outcome states.

    The table is organized as a matrix where:
    - Rows represent right actions (applied first)
    - Columns represent left actions (applied second)
    - Each cell contains the state that results from composing those actions

    For actions a and b, the cell at position (b,a) contains the state that results
    from applying action b followed by action a.

    Attributes:
        data (CayleyTableStatesDataType): Nested dictionary where:
            - Outer keys are right actions (rows)
            - Inner keys are left actions (columns)
            - Values are the resulting states from composing those actions
    """

    # --------------------------------------------------------------------------
    # Initialization
    # --------------------------------------------------------------------------
    def __init__(self):
        self.data: CayleyTableStatesDataType = {}

    # --------------------------------------------------------------------------
    # Table Access
    # --------------------------------------------------------------------------
    def get_row(self, row_label: ActionType) -> CayleyTableStatesRowType:
        """Get all outcomes for a specific right action.

        Args:
            row_label: The right action whose outcomes to retrieve

        Returns:
            Dictionary mapping left actions to their outcome states when composed
            with this right action

        Raises:
            KeyError: If row_label is not found in the table
        """
        if row_label not in self.data:
            raise KeyError(
                f"Row label '{row_label}' not found in table."
                f"Available rows: {list(self.data.keys())}"
            )
        return self.data[row_label]

    def get_column(self, column_label: ActionType) -> CayleyTableStatesRowType:
        """Get all outcomes for a specific left action.

        Args:
            column_label: The left action whose outcomes to retrieve

        Returns:
            Dictionary mapping right actions to their outcome states when composed
            with this left action

        Raises:
            KeyError: If column_label is not found in the table
        """
        first_row = next(iter(self.data.values()))
        if column_label not in first_row:
            raise KeyError(
                f"Column label '{column_label}' not found in table. "
                f"Available columns: {list(first_row.keys())}"
            )
        return {
            row_label: self.data[row_label][column_label] for row_label in self.data
        }

    def get_row_labels(self) -> list[ActionType]:
        """Return the row labels (right actions) of the Cayley table."""
        return list(self.data.keys())

    # --------------------------------------------------------------------------
    # Element Finding
    # --------------------------------------------------------------------------
    def find_equiv_elements(
        self,
        element: ActionType,
        initial_state: StateType,
        world: BaseWorld,
        take_first: bool = False,
    ) -> dict[ActionType, EquivElementsRowColumnDictType]:
        """Find elements that have equivalent behavior to the given element.

        Two elements are considered equivalent if they:
        1. Produce the same outcomes when used as a right action (same row)
        2. Produce the same outcomes when used as a left action (same column)

        Args:
            element: The action to find equivalents for
            initial_state: Starting state for computing outcomes
            world: World in which actions are applied
            take_first: If True, return after finding first equivalent element

        Returns:
            Dictionary mapping equivalent elements to their row/column data
        """
        equiv_elements: dict[ActionType, EquivElementsRowColumnDictType] = {}

        element_row = self.generate_new_element_row(
            element=element, initial_state=initial_state, world=world
        )

        element_column = self.generate_new_element_column(
            element=element, initial_state=initial_state, world=world
        )

        for row_label in self.get_row_labels():
            class_row = self.get_row(row_label)
            class_column = self.get_column(row_label)
            if (element_row == class_row) and (element_column == class_column):
                equiv_elements[row_label] = {"row": class_row, "column": class_column}
                if take_first:
                    return equiv_elements

        return equiv_elements

    # --------------------------------------------------------------------------
    # Table Generation
    # --------------------------------------------------------------------------
    def generate_new_element_row(
        self, element: ActionType, initial_state: StateType, world: BaseWorld
    ) -> CayleyTableStatesRowType:
        """Generate a new row for an element.

        Computes outcomes for the element when used as a right action (applied first)
        in composition with all existing left actions.

        Args:
            element: The right action to generate outcomes for
            initial_state: Starting state for computing outcomes
            world: World in which actions are applied

        Returns:
            Dictionary mapping left actions to outcome states
        """
        element_row = {}
        for col_label in self.get_row_labels():
            action_sequence = col_label + element
            outcome = generate_action_outcome(
                action=action_sequence,
                initial_state=initial_state,
                world=world,
            )
            element_row[col_label] = outcome

        return element_row

    def generate_new_element_column(
        self, element: ActionType, initial_state: StateType, world: BaseWorld
    ) -> CayleyTableStatesRowType:
        """Generate a new column for an element.

        Computes outcomes for the element when used as a left action (applied second)
        in composition with all existing right actions.

        Args:
            element: The left action to generate outcomes for
            initial_state: Starting state for computing outcomes
            world: World in which actions are applied

        Returns:
            Dictionary mapping right actions to outcome states
        """
        element_column = {}
        for row_label in self.get_row_labels():
            action_sequence = element + row_label
            outcome = generate_action_outcome(
                action=action_sequence,
                initial_state=initial_state,
                world=world,
            )
            element_column[row_label] = outcome

        return element_column

    def add_equiv_classes(
        self,
        equiv_classes: EquivClasses,
        initial_state: StateType,
        world: BaseWorld,
    ) -> None:
        """Add new equivalence classes to the table.

        For each class label in the equivalence classes:
        1. Generates a new row (outcomes when used as right action)
        2. Generates a new column (outcomes when used as left action)
        3. Adds these to the table

        Args:
            equiv_classes: The equivalence classes to add
            initial_state: Starting state for computing outcomes
            world: World in which actions are applied
        """
        for class_label in equiv_classes.get_labels():
            self.add_new_element(
                element=class_label,
                initial_state=initial_state,
                world=world,
            )

    def add_new_element(
        self, element: ActionType, initial_state: StateType, world: BaseWorld
    ) -> None:
        """Add a new element to the table.

        Adds both:
        - A new row (outcomes when element is right action)
        - A new column (outcomes when element is left action)

        Args:
            element: The action to add to the table
            initial_state: Starting state for computing outcomes
            world: World in which actions are applied
        """
        # Generate a new row for the Cayley table
        new_row = self.generate_new_element_row(
            element=element,
            initial_state=initial_state,
            world=world,
        )
        # Add the new row to the data.
        self.data[element] = new_row

        # Generate a new column for the Cayley table.
        new_column = self.generate_new_element_column(
            element=element,
            initial_state=initial_state,
            world=world,
        )

        # Add the new column to the data.
        for row_label in self.get_row_labels():
            self.data[row_label][element] = new_column[row_label]

    # --------------------------------------------------------------------------
    # String Representation
    # --------------------------------------------------------------------------
    def __str__(self):
        """Return a string representation of the Cayley table."""
        if not self.data:
            return "\nCayleyTableStates  = {}"
        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")
        # Return the string representation of the DataFrame
        return f"\nCayleyTableStates =\n{df}"
