"""
Manages the mapping between actions and their corresponding action functions.

This module provides a class that maintains a bidirectional mapping between actions
(ActionType) and their associated action functions (ActionFunctionType). It allows for
adding new actions, retrieving actions by length, and looking up actions by their
functions or vice versa.

Type definitions:
    ActionFunctionType: A dictionary mapping StateType to StateType
    DistinctActionsDataType: A dictionary mapping ActionType to ActionFunctionType
"""

from utils.type_definitions import ActionType, StateType

ActionFunctionType = dict[StateType, StateType]
DistinctActionsDataType = dict[ActionType, ActionFunctionType]


class ActionsActionFunctionsMap:
    """
    A class that manages bidirectional mapping between actions and their action
     functions.

    This class maintains a dictionary that maps actions (ActionType) to their
     corresponding action functions (ActionFunctionType). It provides methods to add
     new actions, retrieve actions by length, and perform lookups in both directions
     between actions and their functions.

    Attributes:
        data (DistinctActionsDataType): Dictionary storing the mapping between actions
            and their corresponding action functions.
    """

    def __init__(self) -> None:
        self.data: DistinctActionsDataType = {}

    def add_action(
        self, action: ActionType, action_function: ActionFunctionType
    ) -> None:
        """
        Add an action and its corresponding action function to the mapping.

        Args:
            action (ActionType): The action to be added.
            action_function (ActionFunctionType): The function associated with the
             action.
        """
        self.data[action] = action_function

    def get_actions_from_length(self, length: int) -> list[ActionType]:
        """
        Retrieve all actions that have a specific length.

        Args:
            length (int): The length of actions to retrieve.

        Returns:
            list[ActionType]: A list of actions that have the specified length.
        """
        result: list[ActionType] = []
        for action in self.data:
            if len(action) == length:
                result.append(action)
        return result

    def action_function_exists(self, action_function: ActionFunctionType) -> bool:
        """
        Check if an action function already exists in the mapping.

        Args:
            action_function (ActionFunctionType): The action function to check.

        Returns:
            bool: True if the action function exists, False otherwise.
        """
        return any(
            existing_function == action_function
            for existing_function in self.data.values()
        )

    def get_action_from_action_function(
        self, action_function: ActionFunctionType
    ) -> ActionType:
        """
        Find the representative action for a given action function.

        Args:
            action_function (ActionFunctionType): The action function to look up.

        Returns:
            ActionType: The action associated with the given action function.

        Raises:
            ValueError: If the action function is not found in the mapping.
        """
        for action, existing_function in self.data.items():
            if existing_function == action_function:
                return action
        raise ValueError("Action function not found in self.distinct_actions")

    def get_num_actions(self) -> int:
        """
        Get the total number of distinct actions in the mapping.

        Returns:
            int: The number of distinct actions stored in the data dictionary.
        """
        return len(self.data)

    def get_action_function_from_action(self, action: ActionType) -> ActionFunctionType:
        """
        Return the action function for a given action.

        Args:
            action (ActionType): The action to look up.

        Returns:
            ActionFunctionType: The function associated with the given action.

        Raises:
            KeyError: If the action is not found in the mapping.
        """
        return self.data[action]
