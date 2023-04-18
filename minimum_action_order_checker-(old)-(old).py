"""
This function checks if the size of the Cayley table changes if the order of the minimum actions is changed.

"""
##############################################
from CayleyAgent import CayleyAgent
from Environments.gridworld2D import Gridworld2D
import itertools

##############################################

minimum_actions = ['1', 'R', 'U', 'L', 'D']

information = {}

for permutation in itertools.permutations(minimum_actions, len(minimum_actions)):

    params = {'initial_agent_position': (0, 0),
              'table_size': 3,
              'minimum_actions': list(permutation),
              'world': Gridworld2D(grid_size=(3, 3), wall_positions=[(0.5, 0)]),
              'show_calculation': False,
              }

    agent = CayleyAgent(**params)
    table, state_labelling = agent.generate_cayley_table()
    information[permutation] = table.shape

print(information)

table_size_comparison = {}

for key, value in information.items():
    if value not in table_size_comparison.keys():
        table_size_comparison[value] = []
    table_size_comparison[value].append(key)

print_str = ''
for key in table_size_comparison:
    print_str += '{0}, '.format(key)

print('\n Cayley table sizes: {0}'.format(print_str))
