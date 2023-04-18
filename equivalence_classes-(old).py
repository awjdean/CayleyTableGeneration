import itertools

from Environments.gridworld2D import Gridworld2D


###

def calculateEquivalenceClasses(**parameters):
    initial_agent_position = parameters['initial_agent_position']
    table_size = parameters['table_size']
    minimum_actions = parameters['minimum_actions']
    env = parameters['world']

    information = {'initial_agent_position': initial_agent_position,
                   'equivalence classes': {}}

    # Make self.words into a list of words of size table_size using elements from minimum_actions.
    words = []
    for i in range(1, table_size + 1):
        for combination in itertools.permutations(minimum_actions, i):
            action_sequence = ''
            for element in combination:
                action_sequence += element
            words.append(action_sequence)

    for i in env.states_list:
        information['equivalence classes'][i] = []

    # Find state outcome of action sequences.
    for action_sequence in words:
        env.reset_agent_state(position=initial_agent_position)

        for action in action_sequence[::-1]:
            env.apply_minimum_agent_action(action=action)

        information['equivalence classes'][env.return_agent_position()].append(action_sequence)

    return information


params = {'initial_agent_position': (0, 0),
          'table_size': 3,
          'minimum_actions': ['1', 'L', 'R', 'U', 'D'],
          'world': Gridworld2D(grid_size=(3, 3), wall_positions=[(0.5, 1)])
          }

information = calculateEquivalenceClasses(**params)

params2 = {'initial_agent_position': (0, 0),
           'table_size': 3,
           'minimum_actions': ['1', 'L', 'R', 'U', 'D'],
           'world': Gridworld2D(grid_size=(3, 3), wall_positions=[])
           }

information2 = calculateEquivalenceClasses(**params2)

print(information)
print(information2)
print(information == information2)
