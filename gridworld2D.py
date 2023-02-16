# TODO: world drawer.



def makeWorldCyclical(new_state, grid_size):
    if new_state[0] == -1:
        new_state = (grid_size[0] - 1, new_state[1])

    if new_state[0] == grid_size[0]:
        new_state = (0, new_state[1])

    if new_state[1] == -1:
        new_state = (new_state[0], grid_size[1] - 1)

    if new_state[1] == grid_size[1]:
        new_state = (new_state[0], 0)

    return new_state


def generateTransitionMatrix(grid_size, action_list, wall_positions):
    # TODO: legal wall position checker --> raise exceptions

    # generate agent action look up table
    transition_matrix = {}

    ## no op action ('1')
    action = '1'
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            transition_matrix[(i, j, action)] = (i, j)

    ## move left action ('L')
    action = 'L'
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            new_state = (i - 1, j)
            new_state = makeWorldCyclical(new_state=new_state, grid_size=grid_size)
            transition_matrix[(i, j, action)] = new_state

            if len(wall_positions) > 0:
                for wall in wall_positions:
                    if wall == (
                    i - 0.5, j):  # if there is a wall to the left of the agent then overwrite transition matrix entry.
                        transition_matrix[(i, j, action)] = (i, j)

    ## move right action ('R')
    action = 'R'
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            new_state = (i + 1, j)
            new_state = makeWorldCyclical(new_state=new_state, grid_size=grid_size)
            transition_matrix[(i, j, action)] = new_state

            if len(wall_positions) > 0:
                for wall in wall_positions:
                    if wall == (
                    i + 0.5, j):  # if there is a wall to the right of the agent then overwrite transition matrix entry.
                        transition_matrix[(i, j, action)] = (i, j)

    ## move up action ('U')
    action = 'U'
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            new_state = (i, j + 1)
            new_state = makeWorldCyclical(new_state=new_state, grid_size=grid_size)
            transition_matrix[(i, j, action)] = new_state
            if len(wall_positions) > 0:
                for wall in wall_positions:
                    if wall == (
                    i, j + 0.5):  # if there is a wall above the agent then overwrite transition matrix entry.
                        transition_matrix[(i, j, action)] = (i, j)

    ## move down action ('D')
    action = 'D'
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            new_state = (i, j - 1)
            new_state = makeWorldCyclical(new_state=new_state, grid_size=grid_size)
            transition_matrix[(i, j, action)] = new_state
            if len(wall_positions) > 0:
                for wall in wall_positions:
                    if wall == (
                    i, j - 0.5):  # if there is a wall below the agent then overwrite transition matrix entry.
                        transition_matrix[(i, j, action)] = (i, j)

    return transition_matrix


class Gridworld2D:
    """
    2D gridworld, of size grid_size x grid_size, containing an agent that can take one of five actions:
        no op, move left, move right, move up, move down.
    Gridworld can contain walls; if the agent performs an action that tries to move through a wall the action will have no effect.
    Walls have half integer positions to put them between states.
    """

    def __init__(self, **kwargs):
        """
        :param grid_size: tuple
        :param wall_positions: list of tuples
        """

        self.wall_positions = kwargs.get('wall_positions', [])
        grid_size = kwargs.get('grid_size', (2, 2))

        self._action_list = ['1', 'L', 'R', 'U', 'D']
        self._agent_position = None

        self.states_list = []
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.states_list.append((i, j))

        self.transition_matrix = generateTransitionMatrix(grid_size=grid_size,
                                                          action_list=self._action_list,
                                                          wall_positions=self.wall_positions)

    def resetAgentState(self, position=(0, 0)):
        self._agent_position = position

    def applyAgentAction(self, action):
        if action not in self._action_list:
            raise Exception('action "{}" does not exist.'.format(action))

        # self._agent_position = self.transition_matrix[(self._agent_position[0], self._agent_position[1], action)]
        self._agent_position = self.transition_matrix[(*self._agent_position, action)]

    def returnAgentPosition(self):
        """
        Returns the current position of the agent.
        """
        return self._agent_position

    def drawWorld(self):
        pass
