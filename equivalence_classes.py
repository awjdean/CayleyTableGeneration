from cayley_table_generation.helpers import generate_action_sequence_outcome
from type_definitions import EquivalenceClassesType, MinActionsType, StateType
from worlds.base_world import BaseWorld


class EquivalenceClasses:
    def __init__(self) -> None:
        self.data: EquivalenceClassesType = {}

    def get_labels(self) -> list[str]:
        return list(self.data.keys())

    def add_element(self, element: str, class_label: str):
        self.data[class_label]["elements"].add(element)

    def create_new_class(self, class_label: str, outcome: StateType, split_from=None):
        if class_label in self.data:
            raise ValueError(f"Class with label '{class_label}' already exists.")

        # Create a new class entry
        self.data[class_label] = {
            "elements": {class_label},
            "outcome": outcome,
        }

    def get_class_outcome(self, class_label: str) -> StateType:
        return self.data[class_label]["outcome"]

    def __str__(self):
        return str(self.data)


def generate_initial_equivalence_classes(
    min_actions: MinActionsType, initial_state: StateType, world: BaseWorld
) -> EquivalenceClasses:
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
    equiv_classes = EquivalenceClasses()
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
