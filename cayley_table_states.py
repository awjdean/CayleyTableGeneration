import pandas as pd

from type_definitions import ActionType, CayleyTableStatesDataType


class CayleyTableStates:
    def __init__(self):
        self.data: CayleyTableStatesDataType = {}

    def __str__(self):
        if not self.data:
            return "cayley_table_states: CayleyTableStatesType = {}"

        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")

        # Return the string representation of the DataFrame
        return f"cayley_table_states: CayleyTableStatesType =\n{df}"

    def get_row(self, row_label: ActionType):
        # TODO: check.
        return self.data[row_label]

    def get_column(self, column_label: ActionType):
        # TODO: check.
        return {
            row_label: self.data[row_label][column_label] for row_label in self.data
        }
