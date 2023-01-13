"""
This function checks if the size of the Cayley table changes if the order of the minimum actions is changed.

"""
##############################################
from CayleyTable import CayleyTable
from gridworld2D import Gridworld2D
import itertools

##############################################

parameters = {'minimum_actions': ['1', 'R', 'U', 'L', 'D'],
              'initial_agent_state': (0, 0),
              'world': Gridworld2D(grid_size=(3, 3), wall_positions=[(0.5, 0)]),
              'show_calculation': False}  # TODO: remove from here and put in a print function.


##############################################

def checkMinimumActionOrderAffectOnTableSize(**parameters):
    minimum_actions = parameters['minimum_actions']
    initial_agent_state = parameters['initial_agent_state']
    world = parameters['world']
    show_calculation = parameters['show_calculation']

    results = {}

    for permutation in itertools.permutations(minimum_actions, len(minimum_actions)):
        params = {'initial_agent_state': initial_agent_state,
                  'minimum_actions': list(permutation),
                  'world': world,
                  }

        table = CayleyTable()
        table.generate_cayley_table(**params)

        results[permutation] = table.cayley_table_actions.shape

    return results


##############################################

if __name__ == "__main__":
    results = checkMinimumActionOrderAffectOnTableSize(**parameters)
    print(results)

    ### Print all the different sizes of Cayley table.
    table_size_comparison = {}
    for key, value in results.items():
        if value not in table_size_comparison.keys():
            table_size_comparison[value] = []
        table_size_comparison[value].append(key)

    print_str = ''
    for key in table_size_comparison:
        print_str += '{0}, '.format(key)

    print('\n Cayley table sizes: {0}'.format(print_str))
