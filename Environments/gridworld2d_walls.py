import itertools
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from Environments.gridworld import BaseGridworld, make_world_cyclical, draw_base_gridworld2d, Action2D


class Gridworld2DWalls(BaseGridworld):
    """
    2D gridworld, of size grid_size x grid_size, containing an agent that can take one of five actions:
        no op, move left, move right, move up, move down.
    Gridworld can contain walls; if the agent performs an action that tries to move through a wall the action will have no effect.
    Walls have a half integer position to put them between states.
    """

    def __init__(self, grid_size, initial_agent_position, **kwargs):
        """
        :param grid_size: tuple
        :param wall_positions: list of tuples
        """
        super().__init__(grid_size)
        self._minimum_actions = kwargs.get('minimum_actions', ['1', 'L', 'R', 'U', 'D'])

        self._initial_agent_position = initial_agent_position
        self._current_state = initial_agent_position

        check_variables(grid_size, **kwargs)
        self.wall_strategy = kwargs.get('wall_strategy')
        self._wall_positions = kwargs.get('wall_positions')

        # Walls.
        self._wall_positions = kwargs.get('wall_positions', [])
        self._wall_positions = create_cyclical_pseudo_walls(wall_positions=self._wall_positions,
                                                            grid_size=self._grid_size)

        self._all_states = generate_possible_states(grid_size=self._grid_size)

        self.transition_matrix = generate_transition_matrix(grid_size=self._grid_size,
                                                            all_states=self._all_states,
                                                            minimum_actions=self._minimum_actions,
                                                            wall_positions=self._wall_positions,
                                                            wall_strategy=self.wall_strategy)

    def reset_state(self):
        self._current_state = self._initial_agent_position

    def return_agent_position(self):
        """
        Returns the current position of the agent.
        """
        return self._current_state

    def draw_world(self):

        ax = draw_base_gridworld2d(grid_size=self._grid_size, agent_position=self._current_state)

        # Draw walls.
        if self._wall_positions is not None:
            wall_thickness = 0.25
            wall_plotting_kwargs = {'linewidth': 2,
                                    'edgecolor': 'blue',
                                    'facecolor': 'blue',
                                    'alpha': 1,
                                    'zorder': 3}
            for wall in self._wall_positions:
                if wall[0] // 1 != wall[0]:
                    wall_bottom_left = (wall[0] - wall_thickness / 2, wall[1] - 0.5)
                    rect = Rectangle(xy=wall_bottom_left, width=wall_thickness, height=1, **wall_plotting_kwargs)
                elif wall[1] // 1 != wall[1]:
                    wall_bottom_left = (wall[0] - 0.5, wall[1] - wall_thickness / 2)
                    rect = Rectangle(xy=wall_bottom_left, width=1, height=wall_thickness, **wall_plotting_kwargs)
                else:
                    raise Exception(f"Wall = {wall}.")
                ax.add_patch(rect)

        plt.show()


class Strategy(Enum):
    IDENTITY = 'identity'
    MASKED = 'masked'


def check_variables(grid_size, **kwargs):
    wall_positions = kwargs.get('wall_positions')
    wall_strategy = kwargs.get('wall_strategy')

    # Check wall positions are legal and wall strategy is provided if walls provided.
    if wall_positions is not None:
        try:
            assert len(wall_positions) == 0
        except AssertionError:
            # Check wall strategy provided.
            try:
                assert isinstance(wall_strategy, Strategy)
            except AssertionError:
                raise TypeError("Wall strategy does not exist. Please define a wall strategy.")

            # Check wall positions are legal.
            try:
                for wall in wall_positions:
                    assert (wall[0] % 1 == 0.5 and wall[1] % 1 == 0) or (wall[0] % 1 == 0 and wall[1] % 1 == 0.5)
            except AssertionError:
                raise ValueError(f"Wall position {wall} not legal.")


def outcome_wall(wall_strategy, agent_position, grid_size):
    if wall_strategy == Strategy.IDENTITY:
        # Moving into a wall is same as performing noop action.
        return Action2D('1').apply(position=agent_position, grid_size=grid_size)

    elif wall_strategy == Strategy.MASKED:
        return None

    else:
        raise Exception(f"Wall strategy does not exist. Current wall_strategy: {wall_strategy}.")


def add_walls_to_transition_matrix(transition_matrix, wall_positions, wall_strategy, grid_size):
    """
    Modifies the no walls transition matrix by overwriting the elements in the transition matrix where the agent would
     interact with a wall.
    :param transition_matrix:
    :param wall_positions:
    :param wall_strategy:
    :param grid_size:
    :return:
    """
    if len(wall_positions) > 0:
        for wall in wall_positions:
            # Moving into horizontal blocking wall.
            if wall[0] % 1 == 0.5:
                # Moving right into wall.
                agent_position = (int(wall[0] - 0.5), wall[1])
                # Ignore agent positions with x-values out of range of states.
                if 0 <= agent_position[0] <= grid_size[0] - 1:      # TODO: if this necessary since pseudo walls have been added ? - will this cause incorrect transitions ?
                    # Moving right into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'R')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position,
                                                                             grid_size=grid_size)

                # Moving left into wall.
                agent_position = (int(wall[0] + 0.5), wall[1])
                # Ignore agent positions with x-values out of range of states.
                if 0 <= agent_position[0] <= grid_size[0] - 1:
                    # Moving left into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'L')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position,
                                                                             grid_size=grid_size)

            # Moving into vertical blocking wall.
            if wall[1] % 1 == 0.5:
                # Moving up into wall.
                agent_position = (wall[0], int(wall[1] - 0.5))
                # Ignore agent positions with y-values out of range of states.
                if 0 <= agent_position[1] <= grid_size[1] - 1:
                    # Moving up into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'U')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position,
                                                                             grid_size=grid_size)

                # Moving down into wall.
                agent_position = (wall[0], int(wall[1] + 0.5))
                # Ignore agent positions with y-values out of range of states.
                if 0 <= agent_position[1] <= grid_size[1] - 1:
                    # Moving down into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'D')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position,
                                                                             grid_size=grid_size)
    return transition_matrix


def generate_transition_matrix(grid_size, all_states, minimum_actions, **kwargs):
    wall_positions = kwargs.get('wall_positions')
    wall_strategy = kwargs.get('wall_strategy')

    transition_matrix = generate_no_walls_transition_matrix(grid_size=grid_size,
                                                            all_states=all_states,
                                                            minimum_actions=minimum_actions)
    transition_matrix = add_walls_to_transition_matrix(transition_matrix=transition_matrix,
                                                       wall_positions=wall_positions,
                                                       wall_strategy=wall_strategy,
                                                       grid_size=grid_size)

    return transition_matrix


def create_cyclical_pseudo_walls(wall_positions, grid_size):
    """
    Creates extra 'pseudo' walls to exhibit the cyclical behaviour of the world.
    :param wall_positions:
    :param grid_size:
    :return:
    """
    cyclical_pseudo_walls = []
    for wall in wall_positions:
        cyclical_pseudo_walls.append(make_world_cyclical(position=wall, grid_size=grid_size))
    wall_positions += cyclical_pseudo_walls
    wall_positions = list(set(wall_positions))
    return wall_positions


def generate_possible_states(grid_size):
    """
    # TODO: generalise this to n-dimensional grid.
    Creates a list of all possible states.
    :param grid_size:
    :return:
    """
    possible_states = []
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        possible_states.append((i, j))

    return possible_states


def generate_no_walls_transition_matrix(all_states, minimum_actions, grid_size):
    """
    Create transition matrix for 2D cyclical gridworld with no walls.
    :param minimum_actions:
    :param all_states:
    :param grid_size:
    :return:
    """
    # Initialise agent action look up table
    transition_matrix = {}
    for state, action in itertools.product(all_states, minimum_actions):
        transition_matrix[*state, action] = Action2D(action).apply(position=state, grid_size=grid_size)

    return transition_matrix


if __name__ == '__main__':
    world = Gridworld2DWalls(wall_positions=[],
                             grid_size=(2, 3),
                             initial_agent_position=(0, 0),
                             wall_strategy=Strategy.IDENTITY)

    world2 = Gridworld2DWalls(wall_positions=[(0, -0.5), (-0.5, 0)],
                              grid_size=(2, 3),
                              initial_agent_position=(0, 0),
                              wall_strategy=Strategy.MASKED)

    for key in world.transition_matrix.keys():
        print(f"{key}: {world.transition_matrix[key]},\t{world2.transition_matrix[key]}")

    # world.draw_world()
