from enum import Enum


class AlgebraGenerationMethod(str, Enum):
    STATES_CAYLEY = "states_cayley"
    ACTION_FUNCTION = "action_function"
    LOCAL_ACTION_FUNCTION = "local_action_function"
