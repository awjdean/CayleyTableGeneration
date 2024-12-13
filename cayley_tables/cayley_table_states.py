import pandas as pd

from cayley_tables.equiv_classes import EquivClasses
from cayley_tables.states_cayley_table_generation.action_outcome import (
    generate_action_outcome,
)
from utils.type_definitions import (
    ActionType,
    CayleyTableStatesDataType,
    CayleyTableStatesRowType,
    EquivElementsRowColumnDictType,
    StateType,
)
from worlds.base_world import BaseWorld


class CayleyTableStates:
    def __init__(self):
        self.data: CayleyTableStatesDataType = {}

    def get_row(self, row_label: ActionType) -> CayleyTableStatesRowType:
        if row_label not in self.data:
            raise KeyError(
                f"Row label '{row_label}' not found in table."
                f"Available rows: {list(self.data.keys())}"
            )
        return self.data[row_label]

    def get_column(self, column_label: ActionType) -> CayleyTableStatesRowType:
        first_row = next(iter(self.data.values()))
        if column_label not in first_row:
            raise KeyError(
                f"Column label '{column_label}' not found in table. "
                f"Available columns: {list(first_row.keys())}"
            )
        return {
            row_label: self.data[row_label][column_label] for row_label in self.data
        }

    def __str__(self):
        if not self.data:
            return "\nCayleyTableStates  = {}"
        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")
        # Return the string representation of the DataFrame
        return f"\nCayleyTableStates =\n{df}"

    def get_row_labels(self) -> list[ActionType]:
        """Return the row labels of the Cayley table."""
        return list(self.data.keys())

    def find_equiv_elements(
        self,
        element: ActionType,
        initial_state: StateType,
        world: BaseWorld,
        take_first: bool = False,
    ) -> dict[ActionType, EquivElementsRowColumnDictType]:
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

    def generate_new_element_row(
        self, element: ActionType, initial_state: StateType, world: BaseWorld
    ) -> CayleyTableStatesRowType:
        element_row = {}
        for col_label in self.get_row_labels():
            action_sequence = col_label + element
            # Calculate: a_{col} * (a * w_{0}).
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

    def add_new_element(
        self, element: ActionType, initial_state: StateType, world: BaseWorld
    ) -> None:
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

    def add_equiv_classes(
        self,
        equiv_classes: EquivClasses,
        initial_state: StateType,
        world: BaseWorld,
    ) -> None:
        for class_label in equiv_classes.get_labels():
            self.add_new_element(
                element=class_label,
                initial_state=initial_state,
                world=world,
            )
