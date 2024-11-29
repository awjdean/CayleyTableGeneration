from cayley_table_generation.helpers import generate_action_sequence_outcome
from type_definitions import (
    ActionType,
    EquivClassesDataType,
    MinActionsType,
    StateType,
)
from worlds.base_world import BaseWorld


class EquivClasses:
    def __init__(self) -> None:
        self.data: EquivClassesDataType = {}

    def get_labels(self) -> list[ActionType]:
        return list(self.data.keys())

    def add_element(self, element: ActionType, class_label: ActionType) -> None:
        self.data[class_label]["elements"].add(element)

    def create_new_class(self, class_label: ActionType, outcome: StateType) -> None:
        if class_label in self.data:
            raise ValueError(f"Class with label '{class_label}' already exists.")

        # Create a new class entry
        self.data[class_label] = {
            "elements": {class_label},
            "outcome": outcome,
        }

    def get_class_outcome(self, class_label: ActionType) -> StateType:
        return self.data[class_label]["outcome"]

    def get_all_elements(self) -> list[ActionType]:
        if not self.data:
            return []
        return list(set.union(*[value["elements"] for value in self.data.values()]))

    def get_class_elements(self, class_label: ActionType) -> set[ActionType]:
        return self.data[class_label]["elements"]

    def merge_equiv_class_instances(self, equiv_classes: "EquivClasses") -> None:
        for class_label, class_data in equiv_classes.data.items():
            if class_label in self.data:
                raise ValueError(
                    f"Class with label '{class_label}' already exists in the current "
                    "instance when they should be unique."
                )
            else:
                # Add new class label
                self.data[class_label] = class_data

    def remove_elements_from_classes(self, elements: list[ActionType]) -> None:
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

        # Step 3: Remove elements from the equivalence classes
        for element in elements:
            for class_label, class_data in self.data.items():
                if element in class_data["elements"]:
                    class_data["elements"].remove(element)

    def __str__(self):
        return "\n".join(
            f"{key}: {{ \"outcome\": {value['outcome']}, "
            f"\"elements\": {value['elements']} }}"
            for key, value in self.data.items()
        )


def generate_initial_equivalence_classes(
    min_actions: MinActionsType, initial_state: StateType, world: BaseWorld
) -> EquivClasses:
    """
    Creates initial equivalence classes based on the provided minimum actions
    and the initial state of the world.

    This function iterates through the minimum actions and generates the
    corresponding outcomes for each action. It then compares these outcomes
    with the existing equivalence classes to determine if the action can be
    added to an existing class or if a new class needs to be created.

    Args:
        min_actions (MinActionsType): A collection of minimum actions to be
                                       evaluated.
        initial_state (StateType): The initial state of the world before
                                   any actions are applied.
        world (BaseWorld): An instance of the world in which the actions
                           are applied.

    Returns:
        EquivalenceClasses: An instance of EquivalenceClasses containing
                            the newly created equivalence classes based on
                            the evaluated actions and their outcomes.
    """
    equiv_classes = EquivClasses()
    for a in min_actions:
        # Calculate: \hat{a} * w_{0}.
        a_outcome = generate_action_sequence_outcome(
            action_sequence=a, initial_state=initial_state, world=world
        )
        for b in equiv_classes.get_labels():
            # Calculate: b * w_{0}.
            b_outcome = equiv_classes.get_class_outcome(class_label=b)
            if a_outcome == b_outcome:
                equiv_classes.add_element(element=a, class_label=b)
                break
        else:
            equiv_classes.create_new_class(class_label=a, outcome=a_outcome)

    return equiv_classes
