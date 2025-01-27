import pandas as pd

from utils.errors import CompositionError, ValidationError
from utils.type_definitions import ActionType, CayleyTableActionsDataType


class CayleyTableActions:
    """
    Represents a Cayley table mapping action compositions to their resulting actions.

    The table is organized as a matrix where:
    - Rows represent left actions (applied second)
    - Columns represent right actions (applied first)
    - Each cell contains the label of the equivalence class that results from
      composing those actions

    For actions a and b, the cell at position (b, a) contains the class label for
    the action that results from applying a followed by b on a world state.

    Attributes:
        data (CayleyTableActionsDataType): Nested dictionary where:
            - Outer keys are left actions (rows)
            - Inner keys are right actions (columns)
            - Values are the resulting action class labels
    """

    # --------------------------------------------------------------------------
    # Initialization
    # --------------------------------------------------------------------------
    def __init__(self):
        self.data: CayleyTableActionsDataType = {}

    # --------------------------------------------------------------------------
    # Table Access
    # --------------------------------------------------------------------------
    def get_row_labels(self) -> list[ActionType]:
        """Return the row labels (left actions) of the Cayley table."""
        return list(self.data.keys())

    def get_column_labels(self) -> list[ActionType]:
        """Return the column labels (right actions) of the Cayley table.

        Note: In a well-formed Cayley table, column labels are the same as row labels.
        """
        if not self.data:
            return []
        return list(next(iter(self.data.values())).keys())

    def get_all_actions(self) -> list[ActionType]:
        """Return all unique actions in the Cayley table.

        Returns:
            List of all actions that appear as either row or column labels.
            In a well-formed table, these are the same.
        """
        return self.get_row_labels()

    # --------------------------------------------------------------------------
    # Action Composition
    # --------------------------------------------------------------------------
    def compose_actions(
        self,
        left_action: ActionType,
        right_action: ActionType,
    ) -> ActionType:
        """Compose two actions in sequence: left_action ∘ right_action.

        The composition means "apply right_action to a world state, then apply
         left_action to world state".

        Args:
            left_action: The action applied second (row)
            right_action: The action applied first (column)

        Returns:
            The resulting action class label from the composition

        Raises:
            CompositionError: If either action is not found in the Cayley table
        """
        if left_action not in self.data:
            raise CompositionError(
                f"Cannot compose actions: '{left_action}' not found in Cayley table"
                " rows"
            )
        if right_action not in self.data[left_action]:
            raise CompositionError(
                f"Cannot compose actions: '{right_action}' not found in Cayley table"
                " columns"
            )

        return self.data[left_action][right_action]

    # --------------------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------------------
    def validate(self) -> None:
        """Validate that the Cayley table is well-formed.

        A well-formed Cayley table must have:
        1. The same actions as both row and column labels
        2. Every cell filled with a valid action
        3. All actions that appear as outcomes must also be row/column labels

        Raises:
            ValidationError: If any validation check fails
        """
        if not self.data:
            return

        row_labels = set(self.get_row_labels())
        col_labels = set(self.get_column_labels())

        # Check that row and column labels match
        if row_labels != col_labels:
            raise ValidationError(
                "Cayley table is malformed: row and column labels do not match.\n"
                f"Row labels: {sorted(row_labels)}\n"
                f"Column labels: {sorted(col_labels)}"
            )

        # Check that all outcomes are valid actions
        all_actions = row_labels
        for left_action in self.data:
            for right_action, outcome in self.data[left_action].items():
                if outcome not in all_actions:
                    raise ValidationError(
                        f"Invalid outcome '{outcome}' in Cayley table at "
                        f"position ({left_action}, {right_action}). "
                        f"Must be one of: {sorted(all_actions)}"
                    )

    def to_latex(self) -> str:
        """Convert the Cayley table to a LaTeX longtable format.

        Returns:
            str: LaTeX representation of the Cayley table
        """
        if not self.data:
            return "\\begin{tabular}{c}\nEmpty Cayley Table\\\\\n\\end{tabular}"

        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")

        # Add dollar signs around all elements
        df = df.astype(str)  # Convert all elements to strings first
        df = df.apply(lambda x: "$" + x + "$")
        df.rename(index={idx: f"${idx}$" for idx in df.index}, inplace=True)
        df.rename(columns={col: f"${col}$" for col in df.columns}, inplace=True)

        # Configure the LaTeX output
        latex_str = df.to_latex(
            longtable=True,  # Use longtable for multi-page tables
            index=True,  # Include row labels
            escape=False,  # Don't escape special LaTeX characters
            column_format="l|"  # Left-align first column with vertical line
            + "l" * len(df.columns),  # Left-align other columns
            caption="Insert caption here",  # Add a caption
            position="H",  # Try to place table here
            bold_rows=True,  # Make row headers bold
        )

        # Remove top and bottom rules, move caption to bottom
        latex_str = latex_str.replace("\\toprule\n", "")
        latex_str = latex_str.replace("\\bottomrule\n", "")

        # Move caption to bottom by:
        # 1. Remove existing caption
        latex_str = latex_str.replace(
            "\\caption{Insert caption here} \\\\ \\hline\n", "\\hline\n"
        )
        # 2. Add caption at the end (before \end{longtable})
        latex_str = latex_str.replace(
            "\\end{longtable}", "\\caption{Insert caption here}\n\\end{longtable}"
        )

        return latex_str

    # --------------------------------------------------------------------------
    # String Representation
    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Return a string representation of the Cayley table.

        The table is displayed with:
        - Row indices representing right actions (applied first)
        - Column headers representing left actions (applied second)
        - Each cell showing the result of left_action ∘ right_action

        Returns:
            A formatted string showing the Cayley table as a DataFrame
        """
        if not self.data:
            return "\nCayleyTableActions = {}"

        # Convert the nested dictionary to a pandas DataFrame
        df = pd.DataFrame.from_dict(self.data, orient="index")

        # Add a title row to explain the composition order
        title = "\nCayley Table for Action Composition (a ∘ b):"
        explanation = "- Rows (a): left action, applied second\n"
        explanation += "- Columns (b): right action, applied first\n"
        explanation += "- Cell values: result of composition (a ∘ b)\n"

        return f"{title}\n{explanation}\n{df}"
