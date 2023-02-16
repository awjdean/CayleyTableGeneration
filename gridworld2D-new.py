from typing import NamedTuple, Optional, Tuple, List, Set


class Action:
    NOOP = "1"
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"


class AgentPosition2D(NamedTuple):
    x: int
    y: int

class Wall(NamedTuple):
    x: float
    y: float






def generate_transition_matrix_identity():

    def _wrap(x, y) -> AgentPosition2D:
        return AgentPosition2D(x, y)
    def _get_next_position(position: AgentPosition2D, action: Action):
        if action = Action.NOOP:
            return position
        elif action == Action.UP:
            for wall in wall_positions:


                if wall             # TODO:
                    return position
            return _wrap(position.x, position.y + 1)




def generate_transition_matrix_mask():




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




