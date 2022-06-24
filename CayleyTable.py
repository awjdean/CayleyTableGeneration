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

        ###### Create initial state Cayley table using minimum actions.
        self.cayley_table_states = pd.DataFrame(columns=copy.deepcopy(self.minimum_actions),
                                                index=copy.deepcopy(self.minimum_actions))

        ### Fill initial state Cayley table.
        for table_index_row in range(len(self.cayley_table_states.index)):
            for table_index_column in range(len(self.cayley_table_states.index)):
                right_action_sequence = self.cayley_table_states.index[table_index_row]
                left_action_sequence = self.cayley_table_states.columns[table_index_column]
                action_sequence = left_action_sequence + right_action_sequence

                end_world_state = self.findOutcomeAgent(action_sequence=action_sequence,
                                                        initial_agent_state=self.initial_agent_state,
                                                        world=self.world,
                                                        return_state_outcome=True)

                # Fill in state Cayley table.
                self.cayley_table_states.iat[table_index_row, table_index_column] = end_world_state
        ###

        ### Look for equivalent elements in the state Cayley table.
        equivalents_found = {}
        for element_index in range(len(self.cayley_table_states.index)):
            if element_index in equivalents_found.keys():
                continue

            element_row = list(self.cayley_table_states.iloc[element_index])
            element_column = list(self.cayley_table_states.iloc[:, element_index])

            for comparison_element_index in range(len(self.cayley_table_states.index)):
                if (comparison_element_index == element_index) or (
                        comparison_element_index in equivalents_found.keys()):
                    continue

                comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                if (comparison_element_row == element_row) and (comparison_element_column == element_column):
                    equivalents_found[comparison_element_index] = element_index
        ###

        ### Create initial equivalence classes.
        rows_columns_to_keep = list(range(self.cayley_table_states.shape[0]))
        for i in range(self.cayley_table_states.shape[0]):
            if i not in equivalents_found.keys():
                end_world_state = self.findOutcomeAgent(action_sequence=self.minimum_actions[i],
                                                        initial_agent_state=self.initial_agent_state,
                                                        world=self.world,
                                                        return_state_outcome=True)
                self.equivalence_classes[self.cayley_table_states.index[i]] = {
                    'class_elements': [self.cayley_table_states.index[i]],  # TODO: change list to set().
                    'end_world_state': end_world_state,
                }
                visited_world_states.add(end_world_state)
            else:
                self.equivalence_classes[self.cayley_table_states.index[equivalents_found[i]]]['class_elements'].append(
                    self.cayley_table_states.index[i])
                rows_columns_to_keep.remove(i)

        # Remove equivalent elements from Cayley table.
        self.cayley_table_states = self.cayley_table_states.iloc[rows_columns_to_keep, rows_columns_to_keep]
        ###

        ######

        # Create initial actions Cayley table.
        self.cayley_table_actions = pd.DataFrame(columns=copy.deepcopy(self.cayley_table_states.columns),
                                                 index=copy.deepcopy(self.cayley_table_states.index))

        ###### Fill action Cayley table and identify newly discovered states in states Cayley table.
        new_cayley_table_elements = []
        for table_index_row in range(
                len(self.cayley_table_actions.index)):  # TODO: change Cayley table fill to Cantor set covering method.
            for table_index_column in range(len(self.cayley_table_actions.columns)):
                # Get element from action Cayley table.
                right_action_sequence = self.cayley_table_states.index[table_index_row]
                left_action_sequence = self.cayley_table_states.columns[table_index_column]
                action_sequence = left_action_sequence + right_action_sequence

                # Find state Cayley table row for element.
                state_cayley_table_row = []
                for labelling_element in self.cayley_table_states.index:
                    temp_action_sequence = labelling_element + action_sequence
                    state_cayley_table_row.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                        initial_agent_state=self.initial_agent_state,
                                                                        world=self.world,
                                                                        return_state_outcome=True))

                # Find state Cayley table column for element.
                state_cayley_table_column = []
                for labelling_element in self.cayley_table_states.index:
                    temp_action_sequence = action_sequence + labelling_element
                    state_cayley_table_column.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                           initial_agent_state=self.initial_agent_state,
                                                                           world=self.world,
                                                                           return_state_outcome=True))

                equivalents_found = []
                # Compare row ond column of this element to the rows and columns of the elements in the state Cayley table.
                for comparison_element_index in range(len(self.cayley_table_states.index)):
                    comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                    comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                    if (comparison_element_row == state_cayley_table_row) and (
                            comparison_element_column == state_cayley_table_column):
                        equivalents_found.append(
                            (self.cayley_table_states.index[comparison_element_index], action_sequence))

                if len(equivalents_found) == 0:
                    # Add to new elements list
                    new_cayley_table_elements.append(action_sequence)
                elif len(equivalents_found) == 1:
                    # Add equivalent to the relevant equivalence class
                    self.equivalence_classes[equivalents_found[0][0]]['class_elements'].append(equivalents_found[0][1])

                    # Fill in equivalence table value with the equivalence class label.
                    self.cayley_table_actions.iat[table_index_row, table_index_column] = equivalents_found[0][0]
                else:
                    raise Exception('Too many equivalents !')

        state_cayley_table_row = None
        state_cayley_table_column = None
        equivalents_found = None

        ######

        ######
        while len(new_cayley_table_elements) > 0:
            candidate_element = new_cayley_table_elements.pop(0)

            ###### Check candidate element is not equivalent to other equivalent class labelling elements
            equivalents_found = []
            # Find state Cayley table row for element.
            candidate_state_cayley_table_row = []
            for labelling_element in self.cayley_table_states.index:
                temp_action_sequence = labelling_element + candidate_element
                candidate_state_cayley_table_row.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                              initial_agent_state=self.initial_agent_state,
                                                                              world=self.world,
                                                                              return_state_outcome=True))

            # Find state Cayley table column for element.
            candidate_state_cayley_table_column = []
            for labelling_element in self.cayley_table_states.index:
                temp_action_sequence = candidate_element + labelling_element
                candidate_state_cayley_table_column.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                                 initial_agent_state=self.initial_agent_state,
                                                                                 world=self.world,
                                                                                 return_state_outcome=True))

            # Compare row ond column of this element to the rows and columns of the elements in the state Cayley table.
            for comparison_element_index in range(len(self.cayley_table_states.index)):
                comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                if (comparison_element_row == candidate_state_cayley_table_row) and (
                        comparison_element_column == candidate_state_cayley_table_column):
                    equivalents_found.append(
                        (self.cayley_table_states.index[comparison_element_index], candidate_element))

            if len(equivalents_found) == 1:
                # Add equivalent to the relevant equivalence class
                self.equivalence_classes[equivalents_found[0][0]]['class_elements'].append(equivalents_found[0][1])
                continue
            elif len(equivalents_found) > 1:
                raise Exception('Too many equivalents: {0}'.format(equivalents_found))
            ######

            ###### Check if candidate element breaks equivalence classes. If so, then split those equivalence classes.
            temporary_equivalence_classes = {}
            for equivalence_class_label in self.equivalence_classes.keys():
                # If equivalence class contains a single element, skip it because there are no equivalences to break.
                if len(self.equivalence_classes[equivalence_class_label]['class_elements']) == 1:
                    continue

                # Find outcome of equivalence class labelling element acting on w0 after the candidate element.     # TODO: do I already have this from the equivalence class check ?
                equivalence_class_label_outcome = self.findOutcomeAgent(
                    action_sequence=equivalence_class_label + candidate_element,
                    initial_agent_state=self.initial_agent_state,
                    world=self.world,
                    return_state_outcome=True)

                # Find outcome of equivalence class element acting on w0 after the candidate element.
                for equivalence_class_element in self.equivalence_classes[equivalence_class_label]['class_elements']:
                    equivalence_class_element_outcome = self.findOutcomeAgent(
                        action_sequence=equivalence_class_element + candidate_element,
                        initial_agent_state=self.initial_agent_state,
                        world=self.world,
                        return_state_outcome=True)

                    # If equivalence_class_element produces different result to the class_label_element, then need to split equivalence_class_element into another equivalence class.
                    if equivalence_class_label_outcome != equivalence_class_element_outcome:
                        if len(temporary_equivalence_classes.keys()) == 0:  # TODO: check if this is needed.

                            # Remove equivalence_class_element from original equivalence class.
                            self.equivalence_classes[equivalence_class_label]['class_elements'].remove(
                                equivalence_class_element)  # TODO: check this works as expected.

                            # Create new temporary equivalence class labelled by equivalence_class_element.
                            temporary_equivalence_classes[equivalence_class_element] = {
                                'class_elements': [equivalence_class_element],
                                'end_world_state': self.equivalence_classes[equivalence_class_label]['end_world_state'],
                                'split_from': equivalence_class_label}
                            continue  # TODO: check this works as expected.

                        ### If equivalence_class_element is in any of the temporary equivalence classes, then add it to that class.      # TODO: is checking that (equivalence_class_element \circ candidate_element) = (temp_equivalence_class_label \circ candidate_element) are the same as for the temnporary equivlaence class labels?
                        class_found = False
                        for temp_equivalence_class_label in temporary_equivalence_classes.keys():
                            temp_equivalence_class_label_outcome = self.findOutcomeAgent(
                                action_sequence=temp_equivalence_class_label + candidate_element,
                                initial_agent_state=self.initial_agent_state,
                                world=self.world,
                                return_state_outcome=True)

                            if equivalence_class_element_outcome == temp_equivalence_class_label_outcome:
                                # Remove equivalence_class_element from original equivalence class.
                                self.equivalence_classes[equivalence_class_label]['class_elements'].remove(
                                    equivalence_class_element)
                                # Add equivalence_class_element to temporary equivalence class
                                temporary_equivalence_classes[temp_equivalence_class_label]['class_elements'].append(
                                    equivalence_class_element)
                                class_found = True
                                # break     # TODO: check this.

                        # If equivalence_class_element doesn't belong in any of the temporary equivalence classes, then create a new temporary equivalence class.
                        if not class_found:
                            # Remove equivalence_class_element from original equivalence class.
                            self.equivalence_classes[equivalence_class_label]['class_elements'].remove(
                                equivalence_class_element)

                            # Create new temporary equivalence class labelled by equivalence_class_element.
                            temporary_equivalence_classes[equivalence_class_element] = {
                                'class_elements': [equivalence_class_element],
                                'end_world_state': self.equivalence_classes[equivalence_class_label]['end_world_state'],
                                'split_from': equivalence_class_label}
                    else:
                        continue  # TODO: check this works as expected.

            ######

            ###### Add broken equivalence classes to Cayley table and to self.equivalence_classes
            for temp_equivalence_class_label in temporary_equivalence_classes.keys():
                # Take the column from the state Cayley table that the temp_equivalence_class was split from.
                state_column = self.cayley_table_states[temporary_equivalence_classes['split_from']].to_list()
                # Add column to state Cayley table.
                self.cayley_table_states[temp_equivalence_class_label] = state_column

                # Take the row from the state Cayley table that the temp_equivalence_class was split from.
                state_row = self.cayley_table_states.loc[temporary_equivalence_classes['split_from']].to_list()
                # Calculate the final element in the row.
                state_row.append(
                    self.findOutcomeAgent(action_sequence=(temp_equivalence_class_label + temp_equivalence_class_label),
                                          initial_agent_state=self.initial_agent_state,
                                          world=self.world,
                                          return_state_outcome=True))
                # Add row to state Cayley table.
                self.cayley_table_states.append(data=state_row, name=temp_equivalence_class_label)

            # Merge temporary_equivalence classes into equivalence class dictionary
            self.equivalence_classes = self.equivalence_classes | temporary_equivalence_classes
            ######

            ###### Add candidate_element to the state Cayley table.

            # Find state Cayley table column for element.
            candidate_state_cayley_table_column = []
            for labelling_element in self.cayley_table_states.index:
                candidate_state_cayley_table_column.append(
                    self.findOutcomeAgent(action_sequence=(candidate_element + labelling_element),
                                          initial_agent_state=self.initial_agent_state,
                                          world=self.world,
                                          return_state_outcome=True))
            # Add column to state Cayley table.
            self.cayley_table_states[candidate_element] = candidate_state_cayley_table_column

            # Find state Cayley table row for candidate_element.
            candidate_state_cayley_table_row = {}
            for labelling_element in self.cayley_table_states.index:
                candidate_state_cayley_table_row[labelling_element] = self.findOutcomeAgent(action_sequence=(labelling_element + candidate_element),
                                          initial_agent_state=self.initial_agent_state,
                                          world=self.world,
                                          return_state_outcome=True)
            # Calculate the final element in the row.
            candidate_state_cayley_table_row[candidate_element] = self.findOutcomeAgent(action_sequence=(candidate_element + candidate_element),
                                      initial_agent_state=self.initial_agent_state,
                                      world=self.world,
                                      return_state_outcome=True)
            # Add row to state Cayley table.
            candidate_state_cayley_table_row = pd.Series(candidate_state_cayley_table_row, name=candidate_element)
            candidate_state_cayley_table_row = pd.DataFrame([candidate_state_cayley_table_row], columns=self.cayley_table_states.columns)
            self.cayley_table_states = pd.concat([self.cayley_table_states, candidate_state_cayley_table_row])

            # Create equivalence class for candidate element.
            self.equivalence_classes[candidate_element] = {'class_elements': [candidate_element],
                                                           'end_world_state': self.findOutcomeAgent(
                                                               action_sequence=candidate_element,
                                                               initial_agent_state=self.initial_agent_state,
                                                               world=self.world,
                                                               return_state_outcome=True)}

            ######

            ###### Fill in action Cayley table and identitfy newly discovered states in states Cayley table.






        ######
        # NB: this is a check.
        ### Look for equivalent elements in the state Cayley table.
        equivalents_found = {}
        for element_index in range(len(self.cayley_table_states.index)):
            if element_index in equivalents_found.keys():
                continue

            element_row = list(self.cayley_table_states.iloc[element_index])
            element_column = list(self.cayley_table_states.iloc[:, element_index])

            for comparison_element_index in range(len(self.cayley_table_states.index)):
                if (comparison_element_index == element_index) or (
                        comparison_element_index in equivalents_found.keys()):
                    continue

                comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                if (comparison_element_row == element_row) and (comparison_element_column == element_column):
                    equivalents_found[comparison_element_index] = element_index

        if len(equivalents_found) > 0:
            raise Exception('Too many equivalents: {0}'.format(equivalents_found))
        ######





        pass

        # TODO: add each element to the Cayley table individually:
        #  -1. (DONE) Pop first element from new_cayley_table_elements.
        #  0. (DONE) Check element is not equivalent to other equivalent class labelling elements. If so, return to step -1.
        #  1. (DONE) Check element doesn't break equivalence classes --> if it does then split those equivalence classes.
        #  2. (DONE) Add element to Cayley tables, fill in its state Cayley table entries, and give it an equivalence class.
        #  3. Iterate through the NAN's in the action Cayley table and fill in entries if possible. --> do at end ?
        #      a. If new element(s) found, then append them to new_cayley_table_elements.
        #  4. (DONE) Stop while loop when len(new_cayley_table_elements) == 0.


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
