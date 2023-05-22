import itertools
import matplotlib.pyplot as plt

from Environments.gridworld2D_base import BaseGridworld, draw_base_gridworld2d, MovementAction2D


class Gridworld2DBlock(BaseGridworld):

    def __init__(self, grid_size, initial_agent_position, initial_block_position, **kwargs):
        """
        World states are (agent_position, block_position)
        """
        super().__init__(grid_size)
        check_inputs(grid_size=grid_size,
                     initial_agent_position=initial_agent_position,
                     initial_block_position=initial_block_position,
                     **kwargs)

        self._minimum_actions = kwargs.get('minimum_actions', ['1', 'W', 'E', 'N', 'S'])
        self.initial_agent_position = initial_agent_position
        self._initial_block_position = initial_block_position
        self._current_state = (*self.initial_agent_position, *self._initial_block_position)

        self._possible_states = generate_all_states(grid_size=self._grid_size)

        self.transition_matrix = generate_transition_matrix(possible_states=self._possible_states,
                                                            grid_size=self._grid_size,
                                                            minimum_actions=self._minimum_actions)

    def reset_state(self):
        self._current_state = (*self.initial_agent_position, *self._initial_block_position)

    def return_agent_position(self):
        return self._current_state[0:len(self._grid_size)]

    def return_block_position(self):
        return self._current_state[len(self._grid_size):len(self._grid_size) + len(self._grid_size)]

    def draw_world(self):
        ax = draw_base_gridworld2d(grid_size=self._grid_size, agent_position=self.return_agent_position())

        # Draw block.
        block_position = self.return_block_position()
        side_length = 0.2
        block_plotting_kwargs = {'width': side_length,
                                 'height': side_length,
                                 'facecolor': 'blue',
                                 'edgecolor': 'blue',
                                 'linewidth': 2,
                                 'zorder': 3
                                 }
        bottom_left_coordinates = (block_position[0] - 0.5 * side_length, block_position[1] - 0.5 * side_length)
        rectangle = plt.Rectangle(xy=bottom_left_coordinates, **block_plotting_kwargs)
        ax.add_patch(rectangle)
        ax.text(*block_position, 'B', fontsize=12, color='white', ha='center', va='center')

        plt.show()


def generate_transition_matrix(possible_states, grid_size, minimum_actions):
    transition_matrix = {}
    for state, action in itertools.product(possible_states, minimum_actions):
        block_position = state[2:4]
        agent_position = state[0:2]




        # If the agent moves into the block, then move the block in the same direction as the agent.
        if new_agent_position == block_position:
            new_block_position = MovementAction2D(action).apply(position=block_position, grid_size=grid_size)
        else:
            new_block_position = block_position

        new_state = (*new_agent_position, *new_block_position)

        transition_matrix[(*agent_position, *block_position, action)] = new_state

    return transition_matrix


def generate_all_states(grid_size):
    """

    """
    possible_states = []
    for ax, ay, bx, by in itertools.product(range(grid_size[0]), range(grid_size[1]),
                                            range(grid_size[0]), range(grid_size[1])):
        # Agent and block cannot be in same position.
        if not (ax, ay) == (bx, by):
            possible_states.append((ax, ay, bx, by))

    return possible_states


def check_inputs(grid_size, initial_agent_position, initial_block_position, **kwargs):
    try:
        assert initial_agent_position != initial_block_position
    except AssertionError:
        raise ValueError(f"Block cannot be in same position as agent.")




if __name__ == '__main__':
    # TODO: manually check transition matrix.
    world = Gridworld2DBlock(grid_size=(2, 3),
                             initial_agent_position=(0, 0),
                             initial_block_position=(1, 0))

    for key in world.transition_matrix.keys():
        print(f"{key}: {world.transition_matrix[key]}")
