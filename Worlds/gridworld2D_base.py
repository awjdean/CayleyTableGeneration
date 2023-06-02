import numpy as np
import matplotlib.pyplot as plt
from enum import Enum


class BaseGridworld:

    def __init__(self, grid_size):
        self._current_state = None
        self._minimum_actions = None
        self.transition_matrix = None
        self._grid_size = grid_size

    def apply_minimum_action(self, action):
        try:
            assert action in self._minimum_actions
        except AssertionError:
            raise Exception('action "{}" does not exist.'.format(action))

        # Masked actions.
        if self._current_state is not None:
            self._current_state = self.transition_matrix[(*self._current_state, action)]

    def return_state(self):
        return self._current_state


class Strategy(Enum):
    IDENTITY = 'identity'
    MASKED = 'masked'
    NO_STRATEGY = None

    def apply(self, agent_position, grid_size):
        if self == self.IDENTITY:
            return MovementAction2D('1').apply(position=agent_position, grid_size=grid_size)

        elif self == self.MASKED:
            return None

        elif self == self.NO_STRATEGY:
            raise Exception("Should not be using Strategy.apply() because no Strategy given.")


class MovementAction2D(Enum):
    """
    # TODO: use this for gridworld2D_walls.
    """
    NOOP = '1'
    LEFT = 'W'
    RIGHT = 'E'
    UP = 'N'
    DOWN = 'S'
    CONSUME = 'C'

    def apply(self, position, grid_size):
        if self == self.NOOP:
            return position
        elif self == self.LEFT:
            position = position[0] - 1, position[1]
        elif self == self.RIGHT:
            position = position[0] + 1, position[1]
        elif self == self.UP:
            position = position[0], position[1] + 1
        elif self == self.DOWN:
            position = position[0], position[1] - 1

        position = make_world_cyclical(position=position, grid_size=grid_size)
        return position


def make_world_cyclical(position, grid_size):
    """
    Converts states that are out of the grid size to the relevant cyclical world states.
    :param position:
    :param grid_size:
    :return:
    """
    return tuple(position[i] % grid_size[i] for i in range(len(grid_size)))


def draw_base_gridworld2d(grid_size, agent_position):
    # Create a grid of zeros
    grid = np.zeros((grid_size[1], grid_size[0]))

    # Plot the grid with a circular patch and a rectangle patch
    fig, ax = plt.subplots()
    ax.imshow(grid, cmap='binary', interpolation='nearest', origin='lower',
              extent=[-0.5, grid_size[0] - 1 + 0.5, -0.5, grid_size[1] - 1 + 0.5],
              aspect='equal', vmin=0, vmax=1)

    # Plot agent.
    if agent_position is not None:
        agent_plotting_kwargs = {'radius': 0.1,
                                 'color': 'red',
                                 'fill': True,
                                 'linewidth': 2,
                                 'zorder': 10
                                 }
        circle = plt.Circle(xy=agent_position, **agent_plotting_kwargs)
        ax.add_patch(circle)
        ax.text(*agent_position, "$A$", fontsize=12, color='white', ha='center', va='center', zorder=10)
    else:
        print('Agent position not set so agent not drawn.')

    # Plot circles at integer coordinates.
    circle_plotting_kwargs = {'radius': 0.1,
                              'color': 'black',
                              'zorder': 2
                              }
    for x in range(grid_size[0]):
        for y in range(grid_size[1]):
            circle = plt.Circle(xy=(x, y), **circle_plotting_kwargs)
            ax.add_patch(circle)

    # Plot gridlines.
    ax.set_xticks(np.arange(grid_size[0]))
    ax.set_yticks(np.arange(grid_size[1]))
    plt.grid(color='black', linewidth=1, linestyle='dotted')

    # Remove the axes lines
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return ax
