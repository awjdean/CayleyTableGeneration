from utils.type_definitions import ActionType, StateType

ActionFunctionType = dict[StateType, StateType]
DistinctActionsDataType = dict[ActionType, ActionFunctionType]


class ActionsActionFunctionsMap:
    def __init__(self) -> None:
        self.data: DistinctActionsDataType = {}

    def add_action(
        self, action: ActionType, action_function: ActionFunctionType
    ) -> None:
        """Add an action to the distinct actions dictionary."""
        self.data[action] = action_function

    def get_actions_from_length(self, length: int) -> list[ActionType]:
        result: list[ActionType] = []
        for action in self.data:
            if len(action) == length:
                result.append(action)
        return result

    def action_function_exists(self, action_function: ActionFunctionType) -> bool:
        """Check if an action function already exists in distinct_actions."""
        return any(
            existing_function == action_function
            for existing_function in self.data.values()
        )

    def get_action_from_action_function(
        self, action_function: ActionFunctionType
    ) -> ActionType:
        """Find the representative action for a given action function."""
        for action, existing_function in self.data.items():
            if existing_function == action_function:
                return action
        raise ValueError("Action function not found in self.distinct_actions")

    def get_num_actions(self) -> int:
        """Return the number of distinct actions."""
        return len(self.data)

    def get_action_function_from_action(self, action: ActionType) -> ActionFunctionType:
        """Return the action function for a given action."""
        return self.data[action]
