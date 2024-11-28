import pandas as pd

from type_definitions import ActionType, CayleyTableStatesDataType


class CayleyTableStates:
    def __init__(self):
        self.data: CayleyTableStatesDataType = {}

    def get_row(self, row_label: ActionType):
        if row_label not in self.data:
            raise KeyError(
                f"Row label '{row_label}' not found in table."
                f"Available rows: {list(self.data.keys())}"
            )
        return self.data[row_label]

    def get_column(self, column_label: ActionType):
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
            return "cayley_table_states: CayleyTableStatesType = {}"

        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")

        # Return the string representation of the DataFrame
        return f"cayley_table_states =\n{df}"
