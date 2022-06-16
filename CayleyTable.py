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


#######################################################

class CayleyTable:

    def __init__(self):

        # generateCayleyTable
        self.cayley_table_states = None
        self.cayley_table_actions = None
        self.state_to_action_label = None
        self.action_label_to_state = None
        self.action_to_state = None
        self.equivalence_classes = None
        self.world_params = None

        # checkIdentity
        self.identity_info = None

    def generateCayleyTable(self, **parameters):
        """

        :param parameters:
        :return:
        """
        if self.cayley_table_actions is not None:
            raise Exception('Cayley table already generated. World used: {0}'.format(self.world_params))

        # Unpack function arguments.
        self.minimum_actions = parameters['minimum_actions']
        self.initial_agent_state = parameters['initial_agent_state']
        self.world = parameters['world']
        show_calculation = parameters['show_calculation']  # TODO: remove from here and put in a print function.

        # Save world parameters.
        self.world_params = parameters

        remaining_minimum_actions = copy.deepcopy(self.minimum_actions)
        visited_world_states = set()

        # Create dictionaries.
        self.equivalence_classes = {}  # Keys: actions labelling world states; Elements: actions that appear to be in the same equivalence class (weak equivalence) as the key action.
        # self.action_to_state = {}  # Keys: actions; Elements: world states that the actions cause the agent to reach when the actions are performed on the initial world state.
        # self.action_label_to_state = {}  # Keys: actions labelling world states; Elements: world states those actions label.
        # self.state_to_action_label = {}  # Keys: world states; Elements: actions labeling those world states.



        ##### Create initial Cayley table using minimum actions.
        self.cayley_table_actions = pd.DataFrame(columns=copy.deepcopy(self.minimum_actions),
                                                 index=copy.deepcopy(self.minimum_actions))
        self.cayley_table_states = pd.DataFrame(columns=copy.deepcopy(self.minimum_actions),
                                                index=copy.deepcopy(self.minimum_actions))

        ## Fill initial state Cayley table.
        for table_index_row in range(len(self.cayley_table_states.index)):
            for table_index_column in range(len(self.cayley_table_states.index)):

                right_action_sequence = self.cayley_table_states.index[table_index_row]         # TODO: check these are the correct way around.
                left_action_sequence = self.cayley_table_states.columns[table_index_column]
                action_sequence = left_action_sequence + right_action_sequence

                end_world_state = self.findOutcomeAgent(action_sequence=action_sequence,
                                                        initial_agent_state=self.initial_agent_state,
                                                        world=self.world,
                                                        return_state_outcome=True)

                # Fill in state Cayley table.
                self.cayley_table_states.iat[table_index_row, table_index_column] = end_world_state     # TODO: check indexes are correct way around.


        ## Look for equivalent elements in the state Cayley table.
        equivalents_found = {}
        for element_index in range(len(self.cayley_table_states.index)):
            if element_index in equivalents_found.keys():
                continue

            element_row = list(self.cayley_table_states.iloc[element_index])
            element_column = list(self.cayley_table_states.iloc[:, element_index])

            for comparison_element_index in range(len(self.cayley_table_states.index)):
                if (comparison_element_index == element_index) or (comparison_element_index in equivalents_found.keys()):
                    continue

                comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                if (comparison_element_row == element_row) and (comparison_element_column == element_column):
                    equivalents_found[comparison_element_index] = element_index
        ##

        ## Create initial equivalence classes.
        for i in range(len(self.minimum_actions)):
            if i not in equivalents_found.keys():
                end_world_state = self.findOutcomeAgent(action_sequence=self.minimum_actions[i],
                                                        initial_agent_state=self.initial_agent_state,
                                                        world=self.world,
                                                        return_state_outcome=True)
                self.equivalence_classes[i] = {'end_world_state': end_world_state,
                                               'class_elements': [i]}
                visited_world_states.add(end_world_state)
            else:
                self.equivalence_classes[equivalents_found[i]]['class_elements'].append(i)
                # TODO: Remove equivalent elements from Cayley table


        pass
        ## Identify newly discovered states in states Cayley table

                # Go through Cayley table, when a new state is found, add the relevant action sequence to a list.
















        # # Create initial 1x1 Cayley Table using first minimum action as row and column.
        # action_sequence = remaining_minimum_actions.pop(0)
        # self.cayley_table_actions = pd.DataFrame(columns=[action_sequence],
        #                                          index=[action_sequence])
        # self.cayley_table_states = pd.DataFrame(columns=[action_sequence],
        #                                         index=[action_sequence])
        #
        # ### Create equivalence class for first minimum action
        # end_world_state = self.findOutcomeAgent(action_sequence=action_sequence,
        #                                         initial_agent_state=self.initial_agent_state,
        #                                         world=self.world,
        #                                         return_state_outcome=True)
        #
        # self.equivalence_classes[action_sequence] = {'end_world_state': end_world_state,
        #                                              'class_elements': [action_sequence]}
        # visited_world_states.append(end_world_state)
        # ###
        #
        # ### Calculate outcomes for the Cayley table.
        # table_index = None
        # while True:
        #     # Find which part of the table is being filled in next.
        #     table_index = returnNextIndices(current_index=table_index, table_shape=self.cayley_table_actions.shape)
        #     if table_index == 'End':
        #         break  # TODO: select next action from remaining_minimum_actions
        #
        #     right_action_sequence = self.cayley_table_actions.columns[table_index[0]]  # right_action_sequence = row labels.
        #     left_action_sequence = self.cayley_table_actions.index[table_index[1]]  # left_action_sequence = column labels.
        #     action_sequence = left_action_sequence + right_action_sequence
        #
        #     end_world_state = self.findOutcomeAgent(action_sequence=action_sequence,
        #                                             initial_agent_state=self.initial_agent_state,
        #                                             world=self.world,
        #                                             return_state_outcome=True)
        #     # Fill in state Cayley table.
        #     self.cayley_table_states.iat[table_index[0], table_index[1]] = end_world_state




    def checkIfInEquivalenceClass(self, action_sequence, end_world_state, equivalence_classes, visited_world_states):
        """
        Checks if action_sequence should be in any of the equivalence classes in equivalence_classes.
        :param action_sequence:
        :param end_world_state:
        :param equivalence_classes:
        :param visited_world_states:
        :return: 'None' if not in equivalence class,
        """

        if end_world_state not in visited_world_states:
            # If action_sequence leads to a previously unseen world state then action_sequence must be in its own equivalence class.
            return None
        else:
            # Calculate the state Cayley table row and column for action_sequence as if it was in the state Cayley table:
            new_cayley_row = []











            # for i in (self.cayley_table_actions.columns + [action_sequence]):
            #     self.findOutcomeAgent(action_sequence=i,
            #                           initial_agent_state=self.initial_agent_state,
            #                           world=self.world,
            #                           return_state_outcome=True)
            #
            # new_cayley_column = None

    def isMinimumAction(self, action):
        if action in self.minimum_actions:
            return True
        else:
            return False

            ######################################################
            # ### Calculate outcomes for the Cayley table.
            # table_index = None
            # while True:
            #     # Find which part of the table is being filled in next.
            #     table_index = returnNextIndices(current_index=table_index, table_shape=self.cayley_table_actions.shape)
            #     if table_index == 'End':
            #         break

            # # Create action sequence
            # right_action_sequence = self.cayley_table_actions.columns[
            #     table_index[0]]  # right_action_sequence = row label.
            # left_action_sequence = self.cayley_table_actions.index[
            #     table_index[1]]  # left_action_sequence = column label.
            # action_sequence = left_action_sequence + right_action_sequence

            # Fine outcome of action sequence as a world state.
        #     world.resetAgentState()
        #     for action in action_sequence[::-1]:
        #         world.applyAgentAction(action=action)
        #     end_world_state = world.returnAgentPosition()
        #
        #     if end_world_state not in self.state_to_action_label.keys():
        #         # Add extra column and extra row to Cayley table for the action action_sequence,
        #         # since action_sequence has resulted in encountering a new world state.
        #         row_column_name = copy.deepcopy(action_sequence)
        #         new_row_column = pd.DataFrame(data=([np.nan]),
        #                                       columns=[row_column_name],
        #                                       index=[row_column_name])
        #         self.cayley_table_actions = pd.concat([self.cayley_table_actions, new_row_column])
        #
        #         # Update labelling dictionaries.
        #         self.state_to_action_label[end_world_state] = action_sequence
        #         self.action_label_to_state[action_sequence] = end_world_state
        #
        #     # Record the state that each action results in.
        #     self.action_to_state[action_sequence] = end_world_state
        #
        #     # Insert outcome in the Cayley table (as an action sequence)
        #     if show_calculation:  # TODO: remove from here and put in a print function.
        #         self.cayley_table_actions.iat[table_index[0], table_index[1]] = '{0}.{1} ~ {2}'.format(
        #             left_action_sequence,
        #             right_action_sequence,
        #             self.state_to_action_label[
        #                 end_world_state])
        #     else:
        #         self.cayley_table_actions.iat[table_index[0], table_index[1]] = self.state_to_action_label[
        #             end_world_state]
        # ###

    def findOutcomeAgent(self, action_sequence, world, initial_agent_state, return_state_outcome=True):
        """
        #TODO:
        :param action_sequence:
        :param world:
        :param initial_agent_state:
        :param return_state_outcome:
        :return:
        """

        world.resetAgentState(position=initial_agent_state)
        for action in action_sequence[::-1]:
            world.applyAgentAction(action=action)
        end_world_state = world.returnAgentPosition()

        if return_state_outcome:
            return end_world_state
        else:
            return self.state_to_action_label

    def findOutcomeCayley(self, left_action, right_action=None, return_state_outcome=False):
        """
        Uses the Cayley table to find the outcome of the action sequence: right_action \cdot left_action. The
        outcome is given as the action that labels the state that the action sequence (right_action \cdot
        left_action) would end up as if it was performed from the world state initial_agent_state.

        NB: remember that the right action acts on the world state before the right action.

        :return: Outcome of (right_action \cdot left_action) as the action that labels the state given by:
         right_action \cdot left_action) * initial_agent_state
        """
        if right_action is None:
            state_outcome = self.action_to_state[left_action]
            action_outcome = self.state_to_action_label[state_outcome]
            if return_state_outcome:
                return state_outcome
            else:
                return action_outcome
        else:
            action_outcome = self.cayley_table_actions[left_action][right_action]
            if return_state_outcome:
                state_outcome = self.action_label_to_state[action_outcome]
                return state_outcome
            else:
                return action_outcome

    def checkIdentity(self):
        # Create list of potential left identities from the rows/column headings of the Cayley table.
        left_identities = copy.deepcopy(list(self.cayley_table_actions.index))

        ### Test if e is a left identity (e * a = a).
        for e in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Find the outcome of the LHS of the left identity equation.
                left_outcome_state = self.findOutcomeCayley(left_action=e, right_action=a, return_state_outcome=True)

                # Find the outcome of the RHS of the left identity equation.
                right_outcome_state = self.findOutcomeCayley(left_action=a, return_state_outcome=True)

                # If the left identity equation is not satisfied, then e is not a left identity element and so remove
                # e from the list of possible left identities and stop checking if e satisfies the left identity
                # equation by breaking out of the e loop.
                if left_outcome_state != right_outcome_state:
                    left_identities.remove(
                        e)  # TODO: weird error when trying to stop debugger here, but works if the entire file is run ???
                    # print('{0} removed'.format(e))
                    break
        ###

        # Create list of potential right identities from the rows/column headings of the Cayley table.
        right_identities = copy.deepcopy(list(self.cayley_table_actions.index))

        ### Test if e is a right identity (a * e = a)
        for e in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Find the outcome of the LHS of the right identity equation.
                left_outcome_state = self.findOutcomeCayley(left_action=a, right_action=e, return_state_outcome=True)

                # Find the outcome of the RHS of the right identity equation.
                right_outcome_state = self.findOutcomeCayley(left_action=a, return_state_outcome=True)

                # If the right identity equation is not satisfied, then e is not a right identity element and so
                # remove e from the list of possible right identities and stop checking if e satisfies the right
                # identity equation by breaking out of the e loop.
                if left_outcome_state != right_outcome_state:
                    right_identities.remove(
                        e)  # TODO: weird error when trying to stop debugger here, but works if the entire file is run ???
                    break
        ###

        ### Find any elements that are both a right identity and a left identity.
        identities = []
        for i in left_identities:
            if i in right_identities:
                identities.append(i)
        ###

        self.identity_info = {'left_identities': left_identities,
                              'right_identities': right_identities,
                              'identities': identities}

    def checkInverse(self):
        pass


#######################################################

if __name__ == "__main__":
    table = CayleyTable()

    parameters = {'minimum_actions': ['1', 'U', 'R', 'L', 'D', 'D'],
                  'initial_agent_state': (0, 0),
                  'world': Gridworld2D(grid_size=(2, 2), wall_positions=[(0.5, 0)]),
                  'show_calculation': False}  # TODO: remove from here and put in a print function. # TODO: Error when this is True.
    table.generateCayleyTable(**parameters)
    print('\n')
    print(table.cayley_table_actions)
    # table.checkIdentity()
    print('\n identity_info: {0}'.format(table.identity_info))
