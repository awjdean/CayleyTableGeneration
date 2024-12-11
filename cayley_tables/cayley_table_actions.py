import pandas as pd

from cayley_tables.equiv_classes import EquivClasses
from utils.errors import CompositionError, ValidationError
from utils.type_definitions import ActionType, CayleyTableActionsDataType


class CayleyTableActions:
    def __init__(self):
        self.data: CayleyTableActionsDataType = {}

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
        explanation = "- Rows (b): right action, applied first\n"
        explanation += "- Columns (a): left action, applied second\n"
        explanation += "- Cell values: result of composition (a ∘ b)\n"

        return f"{title}\n{explanation}\n{df}"

    def get_row_labels(self) -> list[ActionType]:
        """Return the row labels (actions) of the Cayley table."""
        return list(self.data.keys())

    def get_column_labels(self) -> list[ActionType]:
        """Return the column labels (actions) of the Cayley table.

        Note: In a well-formed Cayley table, column labels are the same as row labels.
        """
        if not self.data:
            return []
        return list(next(iter(self.data.values())).keys())

    def get_all_actions(self) -> list[ActionType]:
        """Return all unique actions in the Cayley table.

        Returns:
            List of all actions that appear as either row or column labels.
        """
        return self.get_row_labels()

    def compose_actions(
        self, left_action: ActionType, right_action: ActionType
    ) -> ActionType:
        """Compose two actions in sequence: left_action ∘ right_action.

        The composition means "apply right_action, then apply left_action".

        Args:
            left_action: The action applied second (column)
            right_action: The action applied first (row)

        Returns:
            The resulting action from the composition

        Raises:
            CompositionError: If either action is not found in the Cayley table
        """
        if right_action not in self.data:
            raise CompositionError(
                f"Cannot compose actions: '{right_action}' not found in Cayley table"
                " rows"
            )
        if left_action not in self.data[right_action]:
            raise CompositionError(
                f"Cannot compose actions: '{left_action}' not found in Cayley table"
                " columns"
            )

        # For composition (left ∘ right):
        # - right_action is the row (applied first)
        # - left_action is the column (applied second)
        return self.data[right_action][left_action]

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
        for right_action in self.data:
            for left_action, outcome in self.data[right_action].items():
                if outcome not in all_actions:
                    raise ValidationError(
                        f"Invalid outcome '{outcome}' in Cayley table at "
                        f"position ({right_action}, {left_action}). "
                        f"Must be one of: {sorted(all_actions)}"
                    )


def generate_cayley_table_actions(equiv_classes: EquivClasses) -> CayleyTableActions:
    """Generate a Cayley table for action composition from equivalence classes.

    For actions a and b, the composition (a ∘ b) is found by:
    1. Concatenating the actions (a + b)
    2. Finding which equivalence class contains this concatenated action
    3. Using that class's label as the outcome

    The Cayley table is organized with:
    - Rows representing the right action (applied first)
    - Columns representing the left action (applied second)

    Args:
        equiv_classes: The equivalence classes containing action sequences

    Returns:
        A Cayley table mapping action compositions to their outcomes

    Raises:
        CompositionError: If a composed action is not found in any equivalence class
        ValidationError: If the generated table is not well-formed
    """
    cayley_table_actions = CayleyTableActions()

    # For each pair of actions (a,b), compute their composition (a ∘ b)
    for right_action in equiv_classes.get_labels():
        cayley_table_actions.data[right_action] = {}
        for left_action in equiv_classes.get_labels():
            # For composition (left ∘ right), concatenate in reverse order
            # since composition means "apply right_action, then left_action"
            composed_action = left_action + right_action

            # Find which equivalence class contains this composition
            outcome_class_label = equiv_classes.find_element_class(composed_action)
            if outcome_class_label is None:
                raise CompositionError(
                    f"Action composition '{composed_action}' not found in any "
                    "equivalence class.\n"
                    f"Left action: {left_action}\n"
                    f"Right action: {right_action}\n"
                    "This may indicate incomplete equivalence classes or "
                    "an error in the relabeling process."
                )

            cayley_table_actions.data[right_action][left_action] = outcome_class_label

    try:
        cayley_table_actions.validate()
    except ValidationError as e:
        raise ValidationError(f"Generated Cayley table is invalid: {e}")

    return cayley_table_actions
