# TODO: change function names to fit PEP8.

import itertools


def make_world_cyclical(state, grid_size):
    return state[0] % grid_size[0], state[1] % grid_size[1]


from enum import Enum


class Strategy(Enum):
    IDENTITY = 'identity'
    MASKED = 'masked'


def outcome_wall(wall_strategy: Strategy, agent_position):
    if wall_strategy == Strategy.IDENTITY:
        # Moving into a wall is same as performing noop action.
        return agent_position

    if wall_strategy == Strategy.MASKED:
        return None


def add_walls_to_transition_matrix(transition_matrix, wall_positions, wall_strategy, grid_size):

    if len(wall_positions) > 0:
        for wall in wall_positions:
            # Moving into horizontal blocking wall.
            if wall[0] % 1 == 0.5:
                # Moving right into wall.
                agent_position = (wall[0] - 0.5, wall[1])
                # Ignore agent positions with x-values out of range of states.
                if 0 <= agent_position[0] <= grid_size[0] - 1:
                    # Moving right into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'R')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

                # Moving left into wall.
                agent_position = (wall[0] + 0.5, wall[1])
                # Ignore agent positions with x-values out of range of states.
                if 0 <= agent_position[0] <= grid_size[0] - 1:
                    # Moving left into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'L')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

            # Moving into vertical blocking wall.
            if wall[1] % 1 == 0.5:
                # Moving up into wall.
                agent_position = (wall[0], wall[1] - 0.5)
                # Ignore agent positions with y-values out of range of states.
                if 0 <= agent_position[1] <= grid_size[1] - 1:
                    # Moving up into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'U')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

                # Moving down into wall.
                agent_position = (wall[0], wall[1] + 0.5)
                # Ignore agent positions with y-values out of range of states.
                if 0 <= agent_position[1] <= grid_size[1] - 1:
                    # Moving down into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'D')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

    return transition_matrix


def generateTransitionMatrix(**kwargs):
    grid_size = kwargs.get('grid_size')
    action_list = kwargs.get('action_list')
    wall_positions = kwargs.get('wall_positions')
    wall_strategy = kwargs.get('wall_strategy')


    # generate agent action look up table
    transition_matrix = {}

    # no op action ('1')
    action = '1'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        transition_matrix[(i, j, action)] = (i, j)

    # move left action ('L')
    action = 'L'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i - 1, j)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # move right action ('R')
    action = 'R'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i + 1, j)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # move up action ('U')
    action = 'U'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i, j + 1)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # move down action ('D')
    action = 'D'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i, j - 1)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

    # Walls.
    transition_matrix = add_walls_to_transition_matrix(transition_matrix=transition_matrix,
                                                       wall_positions=wall_positions,
                                                       wall_strategy=wall_strategy,
                                                       grid_size=grid_size)

    return transition_matrix


def generate_transition_matrix(**kwargs):
    grid_size = kwargs.get('grid_size')
    action_list = kwargs.get('action_list')
    wall_positions = kwargs.get('wall_positions')

    # generate agent action look up table.
    transition_matrix = {}

    ## no op action ('1')
    action = '1'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        transition_matrix[(i, j, action)] = (i, j)

    ## move left action ('L')
    action = 'L'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i - 1, j)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

        if len(wall_positions) > 0:
            for wall_position in wall_positions:
                # if there is a wall to the left of the agent then L action is same as 1 action.
                if wall_position == (i - 0.5, j):
                    transition_matrix[(i, j, action)] = (i, j)
                    break

    ## move right action ('R')
    action = 'R'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i + 1, j)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state

        if len(wall_positions) > 0:
            for wall_position in wall_positions:
                # if there is a wall to the right of the agent then overwrite transition matrix entry.
                if wall_position == (i + 0.5, j):
                    transition_matrix[(i, j, action)] = (i, j)

    ## move up action ('U')
    action = 'U'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i, j + 1)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state
        if len(wall_positions) > 0:
            for wall_position in wall_positions:
                # if there is a wall above the agent then overwrite transition matrix entry.
                if wall_position == (i, j + 0.5):
                    transition_matrix[(i, j, action)] = (i, j)

    ## move down action ('D')
    action = 'D'
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        new_state = (i, j - 1)
        new_state = make_world_cyclical(state=new_state, grid_size=grid_size)
        transition_matrix[(i, j, action)] = new_state
        if len(wall_positions) > 0:
            for wall_position in wall_positions:
                # if there is a wall below the agent then overwrite transition matrix entry.
                if wall_position == (i, j - 0.5):
                    transition_matrix[(i, j, action)] = (i, j)

    return transition_matrix


def make_walls_cyclical(wall_positions, grid_size):
    """
    Creates extra walls to exhibit the cyclical behaviour of the world.
    :param wall_positions:
    :param grid_size:
    :return:
    """
    cyclical_pseudo_walls = []
    for wall in wall_positions:
        cyclical_pseudo_walls.append(make_world_cyclical(state=wall, grid_size=grid_size))
    wall_positions += cyclical_pseudo_walls
    wall_positions = list(set(wall_positions))
    return wall_positions


class Gridworld2D:
    """
    2D gridworld, of size grid_size x grid_size, containing an agent that can take one of five actions:
        no op, move left, move right, move up, move down.
    Gridworld can contain walls; if the agent performs an action that tries to move through a wall the action will have no effect.
    Walls have a half integer position to put them between states.
    """

    def __init__(self, **kwargs):
        """
        :param grid_size: tuple
        :param wall_positions: list of tuples
        """

        self.wall_strategy = kwargs.get('wall_strategy')
        self._grid_size = kwargs.get('grid_size', (2, 2))

        self._minimum_actions = ['1', 'L', 'R', 'U', 'D']
        self._agent_position = None

        # TODO: legal wall position checker --> raise exceptions
        self._wall_positions = kwargs.get('wall_positions', [])
        self._wall_positions = make_walls_cyclical(wall_positions=self._wall_positions,
                                                   grid_size=self._grid_size)

        self.states_list = []
        for i in range(self._grid_size[0]):
            for j in range(self._grid_size[1]):
                self.states_list.append((i, j))

        self.transition_matrix = generate_transition_matrix(grid_size=self._grid_size,
                                                            action_list=self._minimum_actions,
                                                            wall_positions=self._wall_positions)
        self.transition_matrix2 = generateTransitionMatrix(grid_size=self._grid_size,
                                                           action_list=self._minimum_actions,
                                                           wall_positions=self._wall_positions)

    def reset_agent_state(self, position=(0, 0)):
        self._agent_position = position

    def apply_minimum_agent_action(self, action):
        if action not in self._minimum_actions:
            raise Exception('action "{}" does not exist.'.format(action))

        self._agent_position = self.transition_matrix[(*self._agent_position, action)]

    def return_agent_position(self):
        """
        Returns the current position of the agent.
        """
        return self._agent_position

    def draw_world(self):
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        # Create a grid of zeros
        grid = np.zeros((self._grid_size[1], self._grid_size[0]))

        # Plot the grid with a circular patch and a rectangle patch
        fig, ax = plt.subplots()
        im = ax.imshow(grid, cmap='binary', interpolation='nearest', origin='lower',
                       # extent=[-0.55, self._grid_size[0] - 1 + 0.55, -0.55, self._grid_size[1] - 1 + 0.55],
                       extent=[-0.5, self._grid_size[0] - 1 + 0.5, -0.5, self._grid_size[1] - 1 + 0.5],
                       aspect='equal', vmin=0, vmax=1)

        # Plot agent.
        if self._agent_position is not None:
            agent_plotting_kwargs = {'radius': 0.1,
                                     'color': 'red',
                                     'fill': True,
                                     'linewidth': 2,
                                     'zorder': 3
                                     }
            circle = plt.Circle(xy=self._agent_position, **agent_plotting_kwargs)
            ax.add_patch(circle)
            ax.text(*self._agent_position, 'A', fontsize=12, color='white', ha='center', va='center')
        else:
            print('Agent position not set, so agent not drawn.')

        # Plot walls.
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

        # Plot circles at integer coordinates.
        circle_plotting_kwargs = {'radius': 0.1,
                                  'color': 'black',
                                  'zorder': 2
                                  }
        for x in range(self._grid_size[0]):
            for y in range(self._grid_size[1]):
                circle = plt.Circle(xy=(x, y), **circle_plotting_kwargs)
                ax.add_patch(circle)

        ax.set_xticks(np.arange(self._grid_size[0]))
        ax.set_yticks(np.arange(self._grid_size[1]))
        plt.grid(color='black', linewidth=1, linestyle='dotted')

        # Remove the axes lines
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.show()


if __name__ == '__main__':
    world = Gridworld2D(wall_positions=[(0, -0.5), (-0.5, 0)],
                        grid_size=(3, 2),
                        wall_strategy=Strategy.IDENTITY)
    world.reset_agent_state(position=(0, 0))
    world.draw_world()


    if world.transition_matrix != world.transition_matrix2:
        print(world.transition_matrix == world.transition_matrix2)

        print(f"Key differences:\n\t{world.transition_matrix.keys() - world.transition_matrix2.keys()}\n\t{world.transition_matrix2.keys() - world.transition_matrix.keys()}")
