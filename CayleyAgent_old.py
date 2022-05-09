############################### TO DO #################################

# TODO: check orderings of minimum actions and see if they give different sizes of Cayley table.

# TODO: document this code --> doc strings etc...

# TODO: make world drawer.

# TODO: reduce Cayley table function
## Function that figures out with elements are equivalent in the cayley table and remove one of them.
### Option 1: if that element does not appear anywhere in the table (including in composit action sequences) ?
### Option 2: replace element with another element in all action sequences and see if it makes a difference to the results ?

# TODO: identity element checker
## Check if there exists a single element in the Cayley table that

# TODO: Associativity checker --> a * (b * c) = (a * b) * c

# TODO: inverse checker.

# TODO: Cayley graphs ?

# TODO: non-Euclidean world.

# TODO:

# a * b = b * a


######################################################################

from gridworld2D import Gridworld2D

import itertools
import copy
import numpy as np
import pandas as pd


#######################################################

def returnNextIndices(current_index, table_shape):
    """

    :param table_shape:
    :param current_index: tuple containing two integer elements.
    :return: tuple containing two integer elements.
    """
    if current_index is None:
        return tuple([0, 0])

    current_index = list(current_index)
    if (current_index[0] == 0) and (current_index[1] % 2 == 0):
        if current_index[1] == table_shape[1] - 1:
            return 'End'
        else:
            current_index[1] += 1
    elif (current_index[1] == 0) and (current_index[0] % 2 == 1):
        if current_index[0] == table_shape[0] - 1:
            return 'End'
        else:
            current_index[0] += 1
    elif (current_index[0] % 2 == 0) and (current_index[0] > current_index[1]):
        current_index[1] += 1
    elif (current_index[0] % 2 == 1) and (current_index[0] >= current_index[1]) and (current_index[1] != 0):
        current_index[1] -= 1
    elif (current_index[1] % 2 == 0) and (current_index[0] <= current_index[1]) and (current_index[1] != 0):
        current_index[0] -= 1
    elif (current_index[1] % 2 == 1) and (current_index[0] < current_index[1]):
        current_index[0] += 1
    else:
        raise Exception('Index out of bounds: current_index = {0}'.format(current_index))

    return tuple(current_index)


####################################################


class CayleyTable:
    def __init__(self):
        pass


####################################################


class CayleyAgent:

    def __init__(self, **parameters):
        self.initial_agent_position = parameters['initial_agent_position']
        table_size = parameters['table_size']
        self.minimum_actions = parameters['minimum_actions']
        self.world = parameters['world']
        self.show_calculation = parameters['show_calculation']

    def generateCayleyTable(self):
        """

        :return:
        """

        cayley_table = pd.DataFrame(columns=copy.deepcopy(self.minimum_actions),
                                    index=copy.deepcopy(self.minimum_actions))
        visited_states = []
        state_labelling = {}

        # Put minimum actions in state_labelling dictionary
        for action_sequence in self.minimum_actions:
            self.world.resetAgentState(position=self.initial_agent_position)
            for action in action_sequence[::-1]:
                self.world.applyAgentAction(action=action)

            end_world_state = self.world.returnAgentPosition()
            if end_world_state not in visited_states:
                state_labelling[end_world_state] = action_sequence
                visited_states.append(end_world_state)

        table_index = None
        while True:
            table_index = returnNextIndices(current_index=table_index, table_shape=cayley_table.shape)
            if table_index == 'End':
                break

            right_action_sequence = cayley_table.columns[table_index[0]]  # right_action_sequence = row label.
            left_action_sequence = cayley_table.index[table_index[1]]  # left_action_sequence = column label.

            action_sequence = left_action_sequence + right_action_sequence

            self.world.resetAgentState(position=self.initial_agent_position)
            for action in action_sequence[::-1]:
                self.world.applyAgentAction(action=action)

            end_world_state = self.world.returnAgentPosition()
            if end_world_state not in visited_states:
                row_column_name = copy.deepcopy(action_sequence)
                new_row_column = pd.DataFrame(data=([np.nan]), columns=[row_column_name],
                                              index=[row_column_name])
                cayley_table = pd.concat([cayley_table, new_row_column])

                state_labelling[end_world_state] = action_sequence
                visited_states.append(end_world_state)

            if self.show_calculation:
                cayley_table.iat[table_index[0], table_index[1]] = '{0}.{1} ~ {2}'.format(left_action_sequence,
                                                                                          right_action_sequence,
                                                                                          state_labelling[
                                                                                              end_world_state])
            else:
                cayley_table.iat[table_index[0], table_index[1]] = state_labelling[end_world_state]





        output_dict = {
            'cayley_table': cayley_table,
            'state_to_action_label': state_to_action_label,
            'action_label_to_state': action_label_to_state,
        }

        return output_dict

    def generateEquivalenceClasses(self, action_sequence_length):

        equivalence_classes = {}

        # Make self.words into a list of words of size table_size using elements from minimum_actions.
        words = []
        for i in range(1, action_sequence_length + 1):
            for permutation in itertools.permutations(self.minimum_actions, i):
                action_sequence = ''
                for element in permutation:
                    action_sequence += element
                words.append(action_sequence)

        for i in self.world.states_list:
            equivalence_classes[i] = []

        # Find state outcome of action sequences.
        for action_sequence in words:
            self.world.resetAgentState(position=self.initial_agent_position)

            for action in action_sequence[::-1]:
                self.world.applyAgentAction(action=action)

            equivalence_classes[self.world.returnAgentPosition()].append(action_sequence)

        return equivalence_classes

    def generateWorldStates(self):
        pass

    # def printTable(self):
    #     """
    #     print Cayley table.
    #     :return:
    #     """
    #
    #     with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #         print(str(self.cayley_table))


params = {'initial_agent_position': (0, 0),
          'table_size': 3,
          'minimum_actions': ['1', 'R', 'U', 'L', 'D'],
          'world': Gridworld2D(grid_size=(3, 3), wall_positions=[(0.5, 0)]),
          'show_calculation': False,
          }

agent = CayleyAgent(**params)

table, state_labelling = agent.generateCayleyTable()
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(table)

equivalence_classes = agent.generateEquivalenceClasses(action_sequence_length=3)
print('\n {0}'.format(equivalence_classes))
