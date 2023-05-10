import itertools
from enum import Enum

from gridworld import BaseEnvironment, make_world_cyclical, generate_no_walls_transition_matrix


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


def outcome_wall(wall_strategy, agent_position):
    if wall_strategy == Strategy.IDENTITY:
        # Moving into a wall is same as performing noop action.
        return agent_position

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
                if 0 <= agent_position[0] <= grid_size[0] - 1:
                    # Moving right into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'R')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

                # Moving left into wall.
                agent_position = (int(wall[0] + 0.5), wall[1])
                # Ignore agent positions with x-values out of range of states.
                if 0 <= agent_position[0] <= grid_size[0] - 1:
                    # Moving left into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'L')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

            # Moving into vertical blocking wall.
            if wall[1] % 1 == 0.5:
                # Moving up into wall.
                agent_position = (wall[0], int(wall[1] - 0.5))
                # Ignore agent positions with y-values out of range of states.
                if 0 <= agent_position[1] <= grid_size[1] - 1:
                    # Moving up into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'U')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)

                # Moving down into wall.
                agent_position = (wall[0], int(wall[1] + 0.5))
                # Ignore agent positions with y-values out of range of states.
                if 0 <= agent_position[1] <= grid_size[1] - 1:
                    # Moving down into wall performing wall strategy outcome.
                    transition_matrix[(*agent_position, 'D')] = outcome_wall(wall_strategy=wall_strategy,
                                                                             agent_position=agent_position)
    return transition_matrix


def generate_transition_matrix(grid_size, **kwargs):
    wall_positions = kwargs.get('wall_positions')
    wall_strategy = kwargs.get('wall_strategy')

    transition_matrix = generate_no_walls_transition_matrix(grid_size=grid_size)
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
    Creates a ist of all possible states.
    :param grid_size:
    :return:
    """
    possible_states = []
    for i, j in itertools.product(range(grid_size[0]), range(grid_size[1])):
        possible_states.append((i, j))

    return possible_states

class Gridworld2DWalls(BaseEnvironment):
    """
    2D gridworld, of size grid_size x grid_size, containing an agent that can take one of five actions:
        no op, move left, move right, move up, move down.
    Gridworld can contain walls; if the agent performs an action that tries to move through a wall the action will have no effect.
    Walls have a half integer position to put them between states.
    """

    def __init__(self, grid_size, **kwargs):
        """
        :param grid_size: tuple
        :param wall_positions: list of tuples
        """
        super().__init__()
        self._minimum_actions = kwargs.get('minimum_actions', ['1', 'L', 'R', 'U', 'D'])

        check_variables(grid_size, **kwargs)
        self.wall_strategy = kwargs.get('wall_strategy')
        self._wall_positions = kwargs.get('wall_positions')
        self._grid_size = grid_size

        # Walls.
        self._wall_positions = kwargs.get('wall_positions', [])
        self._wall_positions = create_cyclical_pseudo_walls(wall_positions=self._wall_positions,
                                                            grid_size=self._grid_size)

        self._possible_states = generate_possible_states(grid_size=self._grid_size)

        self.transition_matrix = generate_transition_matrix(grid_size=self._grid_size,
                                                            wall_positions=self._wall_positions,
                                                            wall_strategy=self.wall_strategy)

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
            print('Agent position not set so agent not drawn.')

        # Plot walls.
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
    world = Gridworld2DWalls(wall_positions=[],
                             grid_size=(3, 2),
                             wall_strategy=Strategy.IDENTITY)

    world2 = Gridworld2DWalls(wall_positions=[(0, -0.5), (-0.5, 0)],
                              grid_size=(3, 2),
                              wall_strategy=Strategy.MASKED)

    for key in world.transition_matrix.keys():
        print(f"{key}: {world.transition_matrix[key]},\t{world2.transition_matrix[key]}")

    # world.reset_agent_state(position=(0, 0))
    # world.draw_world()
