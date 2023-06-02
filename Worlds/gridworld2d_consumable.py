import itertools

import matplotlib.pyplot as plt

from Worlds.gridworld2D_base import BaseGridworld, draw_base_gridworld2d, MovementAction2D, Strategy


class Gridworld2DConsumables(BaseGridworld):

    def __init__(self, grid_size, initial_agent_position, initial_consumable_positions, **kwargs):
        """
        :param initial_consumable_positions: initial consumable position as a list of tuples.
        World states as (agent_position, (consumable1_position, consumable1_position2, ...)).
        """
        check_inputs(grid_size, initial_agent_position, initial_consumable_positions, **kwargs)
        super().__init__(grid_size)

        self._minimum_actions = kwargs.get('minimum_actions', ['1', 'W', 'E', 'N', 'S', 'C'])
        self.initial_agent_position = initial_agent_position

        # Consumables
        self._initial_consumables_positions = tuple(initial_consumable_positions)
        self._consumable_strategy = Strategy(kwargs.get('consumable_strategy'))

        self.reset_state()

        self._possible_states = generate_all_states(grid_size=self._grid_size,
                                                    initial_consumables_positions=self._initial_consumables_positions)

        self.transition_matrix = generate_transition_matrix(possible_states=self._possible_states,
                                                            grid_size=self._grid_size,
                                                            minimum_actions=self._minimum_actions,
                                                            consumable_strategy=self._consumable_strategy)

    def reset_state(self):
        self._current_state = (self.initial_agent_position, self._initial_consumables_positions)

    def return_agent_position(self):
        return self._current_state[0]

    def return_consumable_positions(self):
        """
        Returns positions of the remaining consumable as a list of tuples, where each tuple is the position of a
        consumable.
        """
        return self._current_state[1]

    def draw_world(self):
        ax = draw_base_gridworld2d(grid_size=self._grid_size, agent_position=self.return_agent_position())

        # Draw consumables.
        consumables_positions = self.return_consumable_positions()

        consumable_plotting_kwargs = {'radius': 0.15,
                                      'color': 'yellow',
                                      'zorder': 3
                                      }
        for consumable_position in consumables_positions:
            circle = plt.Circle(xy=consumable_position, **consumable_plotting_kwargs)
            ax.add_patch(circle)
            ax.text(*consumable_position, "$C$", fontsize=12, color='black', ha='center', va='center', zorder=3)

        plt.show()


def generate_all_states(grid_size, initial_consumables_positions):
    possible_positions = [(x, y) for x, y in itertools.product(range(grid_size[0]), range(grid_size[1]))]

    possible_states = []
    for agent_position, num_consumables in itertools.product(possible_positions,
                                                             range(0, len(initial_consumables_positions) + 1)):
        for consumable_positions in itertools.product(possible_positions, repeat=num_consumables):
            state = (agent_position, consumable_positions)
            possible_states.append(state)

    return possible_states


def generate_transition_matrix(possible_states, grid_size, minimum_actions, consumable_strategy):
    transition_matrix = {}
    for state, action in itertools.product(possible_states, minimum_actions):
        agent_position = state[0]
        consumables_positions = state[1]

        if action == 'C' and len(consumables_positions) != 0:
            new_state = apply_consume_action(agent_position=agent_position,
                                             consumables_positions=consumables_positions,
                                             grid_size=grid_size,
                                             consumable_strategy=consumable_strategy)
        else:
            new_agent_position = MovementAction2D(action).apply(position=agent_position, grid_size=grid_size)
            new_state = (new_agent_position, consumables_positions)

        # state = convert_list_state_to_tuple_state(list_state=state)
        transition_matrix[*state, action] = new_state

    return transition_matrix


def apply_consume_action(agent_position, consumables_positions, grid_size, consumable_strategy: Strategy):
    if agent_position in consumables_positions:
        new_consumables_positions = list(consumables_positions)
        # Remove a consumable that is in the same position as the agent.
        new_consumables_positions.remove(agent_position)

        new_state = (agent_position, tuple(new_consumables_positions))

    else:
        new_agent_position = consumable_strategy.apply(agent_position=agent_position, grid_size=grid_size)
        if new_agent_position is None:
            new_state = None
        else:
            new_state = (new_agent_position, consumables_positions)

    return new_state


def check_inputs(grid_size, initial_agent_position, initial_consumable_positions, **kwargs):
    """
    Checks inputs are legal.
    """
    try:
        assert len(initial_consumable_positions) == 0
    except AssertionError:
        # Check consumable_strategy provided.
        try:
            assert kwargs.get('consumable_strategy') is not None
        except AssertionError:
            raise NameError(f"consumable_strategy not defined.")


if __name__ == '__main__':
    kwargs = {}
    world = Gridworld2DConsumables(grid_size=(2, 2),
                                   initial_agent_position=(0, 0),
                                   initial_consumable_positions=[(1, 0)],
                                   consumable_strategy='identity')
    world2 = Gridworld2DConsumables(grid_size=(2, 2),
                                    initial_agent_position=(0, 0),
                                    initial_consumable_positions=[(1, 0)],
                                    consumable_strategy='masked')

    for key in world.transition_matrix.keys():
        print(f"{key}: {world.transition_matrix[key]},\t\t{world2.transition_matrix[key]}")

