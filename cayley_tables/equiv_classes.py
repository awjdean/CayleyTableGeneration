from utils.type_definitions import (
    ActionType,
    EquivClassesDataType,
    StateType,
)


class EquivClasses:
    """
    Manages equivalence classes of actions based on their outcomes in a world.

    An equivalence class groups actions that have the same effect when applied to
    a given initial state. Each class has:
    - A label (a representative action)
    - A set of equivalent actions
    - The outcome state when any of these actions are applied

    Attributes:
        data (EquivClassesDataType): Dictionary mapping class labels to their
            elements and outcomes
    """

    # --------------------------------------------------------------------------
    # Initialization
    # --------------------------------------------------------------------------
    def __init__(self) -> None:
        """Initialize an empty equivalence classes structure."""
        self.data: EquivClassesDataType = {}

    # --------------------------------------------------------------------------
    # Class Management
    # --------------------------------------------------------------------------
    def create_new_class(
        self, class_label: ActionType, outcome: StateType, elements: list[ActionType]
    ) -> None:
        """Create a new equivalence class."""
        if class_label in self.data:
            raise ValueError(f"Class with label '{class_label}' already exists.")

        self.data[class_label] = {
            "elements": set(elements),
            "outcome": outcome,
        }

    def merge_equiv_class_instances(self, equiv_classes: "EquivClasses") -> None:
        """Merge another EquivClasses instance into this one."""
        for class_label, class_data in equiv_classes.data.items():
            if class_label in self.data:
                raise ValueError(
                    f"Class with label '{class_label}' already exists in the current "
                    "instance when they should be unique."
                )
            else:
                self.data[class_label] = class_data

    # --------------------------------------------------------------------------
    # Element Management
    # --------------------------------------------------------------------------
    def add_element(self, element: ActionType, class_label: ActionType) -> None:
        """Add an element to an existing equivalence class."""
        if class_label not in self.data:
            raise ValueError(f"Class label '{class_label}' does not exist.")
        self.data[class_label]["elements"].add(element)

    def remove_elements_from_classes(self, elements: list[ActionType]) -> None:
        """Remove actions from their equivalence classes."""
        for element in elements:
            if element in self.data:
                raise ValueError(
                    f"Element '{element}' is a class label and cannot be removed."
                )

        all_elements = self.get_all_elements()
        for element in elements:
            if element not in all_elements:
                raise ValueError(
                    f"Element '{element}' not found in any equivalence class."
                )

        for element in elements:
            for class_label, class_data in self.data.items():
                if element in class_data["elements"]:
                    class_data["elements"].remove(element)

    # --------------------------------------------------------------------------
    # Queries and Lookups
    # --------------------------------------------------------------------------
    def get_labels(self) -> list[ActionType]:
        """Return all equivalence class labels."""
        return list(self.data.keys())

    def get_class_outcome(self, class_label: ActionType) -> StateType:
        """Get the outcome state for an equivalence class."""
        return self.data[class_label]["outcome"]

    def get_all_elements(self) -> list[ActionType]:
        """Get all actions from all equivalence classes."""
        if not self.data:
            return []
        return list(set.union(*[value["elements"] for value in self.data.values()]))

    def get_class_elements(self, class_label: ActionType) -> set[ActionType]:
        """Get all actions in a specific equivalence class."""
        return self.data[class_label]["elements"]

    def get_element_class(self, element: ActionType) -> ActionType | None:
        """Find which equivalence class contains a given action."""
        for class_label, class_data in self.data.items():
            if element in class_data["elements"]:
                return class_label
        return None

    # --------------------------------------------------------------------------
    # Action Sequence Processing
    # --------------------------------------------------------------------------
    # TODO: Implement this method.
    def reduce_action_sequence(self, action_sequence: ActionType) -> ActionType:
        """Reduce action sequence down to a single labelling element."""
        # (1) Check each individual element is a class labelling element.
        ## If individual element is not a class labelling element, then find equivalent
        #  class labelling element.
        # (2) Take pairs of elements
        ##
        return action_sequence

    # --------------------------------------------------------------------------
    # String Representation
    # --------------------------------------------------------------------------
    def __str__(self):
        """Return a string representation of the equivalence classes."""
        if not self.data:
            return "\nEquivClasses = {}"
        return "\nEquivClasses =\n" + "\n".join(
            f"{key}: {{ \"outcome\": {value['outcome']}, "
            f"\"elements\": {value['elements']} }}"
            for key, value in self.data.items()
        )
