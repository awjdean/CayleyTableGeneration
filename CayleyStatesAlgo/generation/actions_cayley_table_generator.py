from utils.cayley_table_actions import CayleyTableActions
from utils.equiv_classes import EquivClasses
from utils.errors import CompositionError, ValidationError
from utils.type_definitions import ActionType


class ActionsCayleyGenerator:
    """
    Generates a Cayley table mapping action compositions to their resulting actions.

    This class builds a complete action composition table by:
    1. Taking equivalence classes as input
    2. Computing all possible compositions between class labels
    3. Finding which class contains each composed action
    4. Validating the resulting table structure

    Attributes:
        equiv_classes: The equivalence classes containing action sequences
        cayley_table_actions: The Cayley table being generated
    """

    def __init__(self, equiv_classes: EquivClasses) -> None:
        """Initialize the generator with equivalence classes.

        Args:
            equiv_classes: The equivalence classes to use for generation
        """
        self.equiv_classes = equiv_classes
        self.cayley_table_actions: CayleyTableActions

    def generate(self) -> CayleyTableActions:
        """Generate the complete Cayley table for action compositions.

        Returns:
            A Cayley table mapping action compositions to their outcomes

        Raises:
            CompositionError: If a composed action is not found in any class
            ValidationError: If the generated table is not well-formed
        """
        self.cayley_table_actions = CayleyTableActions()
        try:
            self._generate_composition_table()
            self.cayley_table_actions.validate()
            return self.cayley_table_actions

        except ValidationError as e:
            raise ValidationError(f"Generated Cayley table is invalid: {e}")

    def _generate_composition_table(self) -> None:
        """Generate the composition table entries.

        For each pair of actions (a, b), computes their composition (a ∘ b) by:
        1. Concatenating the actions by concatinating their strings (a + b)
        2. Finding which equivalence class contains this concatenated action
        3. Using that class's label as the outcome

        Raises:
            CompositionError: If any composed action is not found in a class
        """
        # For each pair of actions (a, b), compute their composition (a ∘ b)
        for left_action in self.equiv_classes.get_labels():
            self.cayley_table_actions.data[left_action] = {}
            for right_action in self.equiv_classes.get_labels():
                outcome_class_label = self._compute_composition(
                    left_action, right_action
                )
                self.cayley_table_actions.data[left_action][right_action] = (
                    outcome_class_label
                )

    def _compute_composition(
        self,
        left_action: ActionType,
        right_action: ActionType,
    ) -> ActionType:
        """Compute a single composition and add it to the table.

        Args:
            left_action: The action applied second
            right_action: The action applied first

        Returns:
            ActionType: The label of the equivalence class containing the composed
              action

        Raises:
            CompositionError: If the composed action is not found in any class
        """
        # For composition (left ∘ right), concatenate in reverse order
        # since composition means "apply right_action, then left_action"
        composed_action = left_action + right_action

        # Find which equivalence class contains this composition
        outcome_class_label = self.equiv_classes.get_element_class(composed_action)
        if outcome_class_label is None:
            raise CompositionError(
                f"Action composition '{composed_action}' not found in any "
                "equivalence class.\n"
                f"Left action: {left_action}\n"
                f"Right action: {right_action}\n"
                "This may indicate incomplete equivalence classes or "
                "an error in the relabeling process."
            )

        return outcome_class_label
