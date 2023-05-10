import itertools


class BaseEnvironment:

    def __init__(self):
        self._agent_position = None
        self._minimum_actions = None
        self.transition_matrix = None


    def return_agent_position(self):
        """
        Returns the current position of the agent.
        """
        return self._agent_position

    def reset_agent_state(self, position=(0, 0)):
        self._agent_position = position

    def apply_minimum_agent_action(self, action):
        try:
            assert action in self._minimum_actions
        except AssertionError:
            raise Exception('action "{}" does not exist.'.format(action))

        # Masked actions.
        if self._agent_position is not None:
            self._agent_position = self.transition_matrix[(*self._agent_position, action)]


def make_world_cyclical(position, grid_size):
    """
    Converts states that are out of the grid size to the relevant cyclical world states.
    :param position:
    :param grid_size:
    :return:
    """
    return tuple(position[i] % grid_size[i] for i in range(len(grid_size)))


def generate_no_walls_transition_matrix(grid_size):
    """
    Create transition matrix for 2D cyclical gridworld with no walls.
    :param grid_size:
    :return:
    """
    # Initialise agent action look up table
    transition_matrix = {}

    # no op action ('1')
    action = '1'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        transition_matrix[(i, j, action)] = (i, j)

    # move left action ('L')
    action = 'L'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i - 1, j)
        new_state = make_world_cyclical(position=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # move right action ('R')
    action = 'R'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i + 1, j)
        new_state = make_world_cyclical(position=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # move up action ('U')
    action = 'U'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i, j + 1)
        new_state = make_world_cyclical(position=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # move down action ('D')
    action = 'D'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i, j - 1)
        new_state = make_world_cyclical(position=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    return transition_matrix
