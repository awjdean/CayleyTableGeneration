"""
# TODO:
    1. Add self.table_ecs dictionary - equivalence class dictionary for Cayley tables elements only.
        * Add self.table_ecs to load and save functions.
    2. Figure out why the Cayley table generating function is producing different results.
        2.1 Tests for Cayley table generating code.
    3. Replace sets with ordered sets.
    4. Improve efficiency of Cayley table generating code. --> NEXT
        - Itertools instead of nested for loops.
"""

from gridworld2D import Gridworld2D

import itertools
import copy
import numpy as np
import pandas as pd
import os
import pickle


# from ordered-set import OrderedSet


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
    INSTANCE_TYPE = 'CayleyTable'

    def __init__(self):

        self.CAYLEY_TABLE_PARAMETERS = None
        self.name = None

        # Class attributes - generate_cayley_table.
        self.cayley_table_states = None
        self.cayley_table_actions = None
        self.ecs = None

    def generate_cayley_table(self, **parameters):
        """

        :param parameters:
        :return:
        """
        if (self.cayley_table_actions is not None) or (self.cayley_table_states is not None):
            raise Exception('Cayley table already generated. World used: {0}'.format(self.CAYLEY_TABLE_PARAMETERS))

        # Unpack function arguments.
        MINIMUM_ACTIONS = parameters['minimum_actions']
        INITIAL_AGENT_STATE = parameters['initial_agent_state']
        WORLD = parameters['world']

        # Save world parameters.
        self.CAYLEY_TABLE_PARAMETERS = parameters

        remaining_minimum_actions = copy.deepcopy(MINIMUM_ACTIONS)
        visited_world_states = set()

        # Create equivalence classes dictionary.
        # Create dictionaries. Keys: actions labelling world states; Elements: actions that appear to be in the same
        # equivalence class (weak equivalence) as the key action.
        self.ecs = {}

        ################################################################################################################
        # Create initial state Cayley table using minimum actions.
        ################################################################################################################
        self.cayley_table_states = pd.DataFrame(columns=copy.deepcopy(MINIMUM_ACTIONS),
                                                index=copy.deepcopy(MINIMUM_ACTIONS))

        ### Fill initial state Cayley table.
        for table_index_row in range(len(self.cayley_table_states.index)):
            for table_index_column in range(len(self.cayley_table_states.index)):
                right_action_sequence = self.cayley_table_states.index[table_index_row]
                left_action_sequence = self.cayley_table_states.columns[table_index_column]
                action_sequence = left_action_sequence + right_action_sequence

                end_world_state = self.findOutcomeAgent(action_sequence=action_sequence,
                                                        initial_agent_state=INITIAL_AGENT_STATE,
                                                        world=WORLD,
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
                end_world_state = self.findOutcomeAgent(action_sequence=MINIMUM_ACTIONS[i],
                                                        initial_agent_state=INITIAL_AGENT_STATE,
                                                        world=WORLD,
                                                        return_state_outcome=True)
                self.ecs[self.cayley_table_states.index[i]] = {
                    'class_elements': set([self.cayley_table_states.index[i]]),
                    'end_world_state': end_world_state,
                }
                visited_world_states.add(end_world_state)
            else:
                self.ecs[self.cayley_table_states.index[equivalents_found[i]]]['class_elements'].add(
                    self.cayley_table_states.index[i])
                rows_columns_to_keep.remove(i)

        # Remove equivalent elements from Cayley table.
        self.cayley_table_states = self.cayley_table_states.iloc[rows_columns_to_keep, rows_columns_to_keep]
        ###

        ################################################################################################################
        # Identify newly discovered states in states Cayley table, and add equivalent states to the relevant equivalence classes.
        ################################################################################################################
        cayley_table_candidate_elements = set()
        # TODO: change Cayley table fill to Cantor set covering method.
        for table_index_row in range(len(self.cayley_table_states.index)):
            for table_index_column in range(len(self.cayley_table_states.columns)):
                # Get labelling elements from Cayley table.
                right_action_sequence = self.cayley_table_states.index[table_index_row]
                left_action_sequence = self.cayley_table_states.columns[table_index_column]
                action_sequence = left_action_sequence + right_action_sequence

                # Find state Cayley table row for element.
                state_cayley_table_row = []
                for labelling_element in self.cayley_table_states.index:
                    temp_action_sequence = labelling_element + action_sequence
                    state_cayley_table_row.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                        initial_agent_state=INITIAL_AGENT_STATE,
                                                                        world=WORLD,
                                                                        return_state_outcome=True))

                # Find state Cayley table column for element.
                temp_ec_label_state_cayley_table_column = []
                for labelling_element in self.cayley_table_states.index:
                    temp_action_sequence = action_sequence + labelling_element
                    temp_ec_label_state_cayley_table_column.append(
                        self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                              initial_agent_state=INITIAL_AGENT_STATE,
                                              world=WORLD,
                                              return_state_outcome=True))

                equivalents_found = set()
                # Compare row ond column of this element to the rows and columns of the elements in the state Cayley table.
                for comparison_element_index in range(len(self.cayley_table_states.index)):
                    comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                    comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                    if (comparison_element_row == state_cayley_table_row) and (
                            comparison_element_column == temp_ec_label_state_cayley_table_column):
                        equivalents_found.add(
                            (self.cayley_table_states.index[comparison_element_index], action_sequence))

                if len(equivalents_found) == 0:
                    # Add to new elements list
                    cayley_table_candidate_elements.add(action_sequence)
                elif len(equivalents_found) == 1:
                    # Add equivalent to the relevant equivalence class
                    self.ecs[list(equivalents_found)[0][0]]['class_elements'].add(list(equivalents_found)[0][1])
                else:
                    raise Exception('Too many equivalents !')

        state_cayley_table_row = None
        temp_ec_label_state_cayley_table_column = None
        equivalents_found = None
        ################################################################################################################

        while len(cayley_table_candidate_elements) > 0:
            print('Num cayley_table_candidate_elements remaining: {0}'.format(len(cayley_table_candidate_elements)),
                  end='\r')
            candidate_element = cayley_table_candidate_elements.pop()

            ############################################################################################################
            # Check candidate element is not equivalent to other equivalent class labelling elements
            ############################################################################################################
            equivalents_found = []
            # Find state Cayley table row for element.
            candidate_state_cayley_table_row = []
            for labelling_element in self.cayley_table_states.index:
                temp_action_sequence = labelling_element + candidate_element
                candidate_state_cayley_table_row.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                              initial_agent_state=INITIAL_AGENT_STATE,
                                                                              world=WORLD,
                                                                              return_state_outcome=True))

            # Find state Cayley table column for element.
            candidate_state_cayley_table_column = []
            for labelling_element in self.cayley_table_states.index:
                temp_action_sequence = candidate_element + labelling_element
                candidate_state_cayley_table_column.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                                 initial_agent_state=INITIAL_AGENT_STATE,
                                                                                 world=WORLD,
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
                # Add equivalent to the relevant equivalence class.
                self.ecs[equivalents_found[0][0]]['class_elements'].add(equivalents_found[0][1])
                continue
            elif len(equivalents_found) > 1:
                raise Exception('Too many equivalents: {0}'.format(equivalents_found))

            ############################################################################################################
            # Check if the candidate element breaks equivalence classes.
            #   If so, then split those equivalence classes.
            #   To check if the candidate element breaks an equivalence class labelled by an element (l):
            #       1. Find the outcome of (l) \circ ( (c) * w0 ).
            #       2. For each equivalence class element (e), find the outcome of (e) \circ ( (c) * w0 ).
            #       3. If (l) \circ ( (c) * w0 ) != (e) \circ ( (c) * w0 ), then the candidate element breaks the
            #       equivalence class and equivalence class element (e) needs to be split into its own equivalence
            #       class.
            ############################################################################################################
            temp_ecs = {}
            for ec_label in self.ecs.keys():
                # If equivalence class contains a single element, skip it because there are no equivalences to break.
                if len(self.ecs[ec_label]['class_elements']) == 1:
                    continue

                # Find outcome of equivalence class labelling element acting on w0 after the candidate element.     # TODO: do I already have this from the equivalence class check ?
                ec_label_outcome = self.findOutcomeAgent(
                    action_sequence=(ec_label + candidate_element),
                    initial_agent_state=INITIAL_AGENT_STATE,
                    world=WORLD,
                    return_state_outcome=True)

                # Find outcome of each equivalence class element acting on w0 after the candidate element.
                for ec_element in copy.deepcopy(
                        self.ecs[ec_label]['class_elements']):  # TODO: convert to list ?
                    ec_element_outcome = self.findOutcomeAgent(
                        action_sequence=(ec_element + candidate_element),
                        initial_agent_state=INITIAL_AGENT_STATE,
                        world=WORLD,
                        return_state_outcome=True)

                    # If ec_element produces different result to the class_label_element, then need to split ec_element into another equivalence class.
                    if ec_label_outcome != ec_element_outcome:
                        ### If ec_element is in any of the temporary equivalence classes, then add it to that class.      # TODO: is checking that (ec_element \circ candidate_element) = (temp_ec_label \circ candidate_element) are the same as for the temnporary equivlaence class labels?
                        flag_temp_ec_found = False
                        for temp_ec_label in temp_ecs.keys():
                            # To be in the same temporary equivalence class, elements must be split from the same equivalence class.
                            if temp_ecs[temp_ec_label]['split_from'] != ec_label:
                                continue

                            temp_ec_label_outcome = self.findOutcomeAgent(
                                action_sequence=temp_ec_label + candidate_element,
                                initial_agent_state=INITIAL_AGENT_STATE,
                                world=WORLD,
                                return_state_outcome=True)

                            if ec_element_outcome == temp_ec_label_outcome:
                                # Remove ec_element from original equivalence class.
                                self.ecs[ec_label]['class_elements'].remove(ec_element)
                                # Add ec_element to temporary equivalence class
                                temp_ecs[temp_ec_label]['class_elements'].add(ec_element)
                                flag_temp_ec_found = True
                                break

                        # If ec_element doesn't belong in any of the temporary equivalence classes, then create a new temporary equivalence class.
                        if not flag_temp_ec_found:
                            # Remove ec_element from original equivalence class.
                            self.ecs[ec_label]['class_elements'].remove(ec_element)

                            # Create new temporary equivalence class labelled by ec_element.
                            temp_ecs[ec_element] = {
                                'class_elements': set([ec_element]),
                                'end_world_state': self.ecs[ec_label]['end_world_state'],
                                'split_from': ec_label}

            ############################################################################################################
            # Add broken equivalence classes to Cayley table and to self.ecs
            ############################################################################################################
            # TODO: change so that this copies the rows and columns of the 'split_from' equivalence class ? --> remember to copy !
            for temp_ec_label in temp_ecs.keys():
                # Find state Cayley table column for temp_ec_label element.
                temp_ec_label_state_cayley_table_column = []
                for labelling_element in self.cayley_table_states.index:
                    temp_ec_label_state_cayley_table_column.append(
                        self.findOutcomeAgent(action_sequence=(temp_ec_label + labelling_element),
                                              initial_agent_state=INITIAL_AGENT_STATE,
                                              world=WORLD,
                                              return_state_outcome=True))
                # Check this is the same as the row for split_from equivalence class.
                if not temp_ec_label_state_cayley_table_column == self.cayley_table_states[
                    temp_ecs[temp_ec_label]['split_from']].to_list():
                    raise Exception('columns do not match')
                # Add column to state Cayley table.
                self.cayley_table_states[temp_ec_label] = temp_ec_label_state_cayley_table_column

                # Find state Cayley table row for temp_ec_label element.
                temp_ec_label_state_cayley_table_row = {}
                for labelling_element in self.cayley_table_states.columns:
                    if labelling_element == temp_ec_label:
                        continue
                    temp_ec_label_state_cayley_table_row[labelling_element] = self.findOutcomeAgent(
                        action_sequence=(labelling_element + temp_ec_label),
                        initial_agent_state=INITIAL_AGENT_STATE,
                        world=WORLD,
                        return_state_outcome=True)
                # Calculate the final element in the row.
                temp_ec_label_state_cayley_table_row[temp_ec_label] = self.findOutcomeAgent(
                    action_sequence=(temp_ec_label + temp_ec_label),
                    initial_agent_state=INITIAL_AGENT_STATE,
                    world=WORLD,
                    return_state_outcome=True)
                # Add row to state Cayley table.
                temp_ec_label_state_cayley_table_row = pd.Series(temp_ec_label_state_cayley_table_row,
                                                                 name=temp_ec_label)
                temp_ec_label_state_cayley_table_row = pd.DataFrame([temp_ec_label_state_cayley_table_row],
                                                                    columns=self.cayley_table_states.columns)
                self.cayley_table_states = pd.concat([self.cayley_table_states, temp_ec_label_state_cayley_table_row])

            # Merge temporary_equivalence classes into equivalence class dictionary
            if len(temp_ecs.keys()) > 0:
                print('Equivalence class(es) split. Candidate element: {0}.\n    temp_ecs:'.format(candidate_element))
                for i in temp_ecs.keys():
                    print('    {0}'.format(temp_ecs[i]))
            self.ecs = self.ecs | temp_ecs

            ############################################################################################################
            # Add candidate_element to the state Cayley table.
            ############################################################################################################
            # Find state Cayley table column for element.
            candidate_state_cayley_table_column = []
            for labelling_element in self.cayley_table_states.index:
                candidate_state_cayley_table_column.append(
                    self.findOutcomeAgent(action_sequence=(candidate_element + labelling_element),
                                          initial_agent_state=INITIAL_AGENT_STATE,
                                          world=WORLD,
                                          return_state_outcome=True))
            # Add column to state Cayley table.
            self.cayley_table_states[candidate_element] = candidate_state_cayley_table_column

            # Find state Cayley table row for candidate_element.
            candidate_state_cayley_table_row = {}
            for labelling_element in self.cayley_table_states.columns:
                if labelling_element == candidate_element:
                    continue
                candidate_state_cayley_table_row[labelling_element] = self.findOutcomeAgent(
                    action_sequence=(labelling_element + candidate_element),
                    initial_agent_state=INITIAL_AGENT_STATE,
                    world=WORLD,
                    return_state_outcome=True)
            # Calculate the final element in the row.
            candidate_state_cayley_table_row[candidate_element] = self.findOutcomeAgent(
                action_sequence=(candidate_element + candidate_element),
                initial_agent_state=INITIAL_AGENT_STATE,
                world=WORLD,
                return_state_outcome=True)
            # Add row to state Cayley table.
            candidate_state_cayley_table_row = pd.Series(candidate_state_cayley_table_row, name=candidate_element)
            candidate_state_cayley_table_row = pd.DataFrame([candidate_state_cayley_table_row],
                                                            columns=self.cayley_table_states.columns)
            self.cayley_table_states = pd.concat([self.cayley_table_states, candidate_state_cayley_table_row])

            # Create equivalence class for candidate element.
            self.ecs[candidate_element] = {'class_elements': set([candidate_element]),
                                           'end_world_state': self.findOutcomeAgent(
                                               action_sequence=candidate_element,
                                               initial_agent_state=INITIAL_AGENT_STATE,
                                               world=WORLD,
                                               return_state_outcome=True)}

            ############################################################################################################
            # Go through (entire) state Cayley table and find new elements          # TODO: this is a nasty brute force method --> should be improved.
            ############################################################################################################
            for table_index_row in range(len(self.cayley_table_states.index)):
                for table_index_column in range(len(self.cayley_table_states.columns)):
                    # Get labelling elements from Cayley table.
                    right_action_sequence = self.cayley_table_states.index[
                        table_index_row]  # TODO: ask Laure about this.
                    left_action_sequence = self.cayley_table_states.columns[table_index_column]
                    action_sequence = left_action_sequence + right_action_sequence

                    # Find state Cayley table row for element.
                    state_cayley_table_row = []
                    for labelling_element in self.cayley_table_states.index:
                        temp_action_sequence = labelling_element + action_sequence
                        state_cayley_table_row.append(self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                                            initial_agent_state=INITIAL_AGENT_STATE,
                                                                            world=WORLD,
                                                                            return_state_outcome=True))

                    # Find state Cayley table column for element.
                    temp_ec_label_state_cayley_table_column = []
                    for labelling_element in self.cayley_table_states.index:
                        temp_action_sequence = action_sequence + labelling_element
                        temp_ec_label_state_cayley_table_column.append(
                            self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                  initial_agent_state=INITIAL_AGENT_STATE,
                                                  world=WORLD,
                                                  return_state_outcome=True))

                    equivalents_found = set()  # TODO: figure out the best way to deal with this - list, set, dictionary ?
                    # Compare row ond column of this element to the rows and columns of the elements in the state Cayley table.
                    for comparison_element_index in range(len(self.cayley_table_states.index)):
                        comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
                        comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])

                        if (comparison_element_row == state_cayley_table_row) and (
                                comparison_element_column == temp_ec_label_state_cayley_table_column):
                            equivalents_found.add(
                                (self.cayley_table_states.index[comparison_element_index], action_sequence))

                    if len(equivalents_found) == 0:
                        # Add to new elements list
                        cayley_table_candidate_elements.add(action_sequence)
                    elif len(equivalents_found) == 1:
                        # Add equivalent to the relevant equivalence class
                        self.ecs[list(equivalents_found)[0][0]]['class_elements'].add(list(equivalents_found)[0][1])
                    else:
                        raise Exception('Too many equivalents !')
            ############################################################################################################

        ################################################################################################################
        # CHECK for equivalent elements in the state Cayley table --> there should be none.
        ################################################################################################################
        equivalents_found = {}  # TODO: change to set containing tuples ?
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

        ################################################################################################################
        # CHECK that each element is only in one equivalence class.
        ################################################################################################################

        ### Select element in equivalence class.
        for labelling_element in self.ecs.keys():
            for check_element in self.ecs[labelling_element]['class_elements']:
                ec_of_matching_elements = []
                ###
                ### Check if element is the same as any of the other elements in this equivalence class.
                for comparison_element in self.ecs[labelling_element]['class_elements']:
                    if check_element == comparison_element:
                        ec_of_matching_elements.append(labelling_element)
                ###

                # Check if element is in any other equivalence class.
                for comparison_labelling_element in self.ecs.keys():
                    # Already checked elements in same equivalence class.
                    if comparison_labelling_element == labelling_element:
                        continue
                    for comparison_element in self.ecs[comparison_labelling_element]['class_elements']:
                        if check_element == comparison_element:
                            ec_of_matching_elements.append(comparison_labelling_element)

                if (len(ec_of_matching_elements) != 1) and (
                        ec_of_matching_elements[0] != labelling_element):
                    raise Exception(
                        'Element in more than one equivalence class. \nEquivalence_class_of_matching_elements = {0}'.format(
                            ec_of_matching_elements))

        ################################################################################################################
        # Relabel equivalence classes with their shortest label and change the relevant Cayley table row-column labels.
        ################################################################################################################

        cayley_table_relabelling_dict = {}
        old_ec_labels = list(self.ecs.keys())
        for ec_label in old_ec_labels:
            # Sort equivalence class elements by alphabetical order and length order.
            sorted_ec_elements = sorted(list(self.ecs[ec_label]['class_elements']))
            sorted_ec_elements = sorted(sorted_ec_elements, key=len)

            # New labelling element is first element in sorted_ec_elements.
            new_ec_label = sorted_ec_elements[0]

            # Store relabelling.
            cayley_table_relabelling_dict[ec_label] = new_ec_label

            # Relabel equivalence class.
            self.ecs[new_ec_label] = self.ecs.pop(ec_label)
            self.ecs[new_ec_label]['class_elements'] = sorted_ec_elements

        # Relabel state Cayley table.
        self.cayley_table_states = self.cayley_table_states.rename(columns=cayley_table_relabelling_dict,
                                                                   # TODO: check this works.
                                                                   index=cayley_table_relabelling_dict)

        ################################################################################################################
        # Order state Cayley table rows and columns according to same ordering as equivalence classes were relabeled.
        ################################################################################################################
        cayley_tables_row_columns = list(self.cayley_table_states.index)
        sorted_cayley_tables_row_columns = sorted(cayley_tables_row_columns)
        sorted_cayley_tables_row_columns = sorted(sorted_cayley_tables_row_columns, key=len)

        self.cayley_table_states = self.cayley_table_states.reindex(index=sorted_cayley_tables_row_columns,
                                                                    columns=sorted_cayley_tables_row_columns)

        ################################################################################################################
        # Create and fill action Cayley table.
        ################################################################################################################

        # create action Cayley table.
        self.cayley_table_actions = pd.DataFrame(columns=self.cayley_table_states.columns,
                                                 index=self.cayley_table_states.index)
        self.cayley_table_ecs = {}

        # Fill action Cayley table.
        for table_index_row in range(len(self.cayley_table_actions.index)):
            for table_index_column in range(len(self.cayley_table_actions.columns)):
                is_filled_flag = False
                # Get labelling elements from Cayley table.
                right_action_sequence = self.cayley_table_states.index[table_index_row]  # TODO: ask Laure about this.
                left_action_sequence = self.cayley_table_states.columns[table_index_column]
                candidate_element = left_action_sequence + right_action_sequence

                # Find label of equivalence class containing action_sequence, then use that label in the actions Cayley table.
                for labelling_element in self.ecs.keys():
                    for ec_element in self.ecs[labelling_element]['class_elements']:
                        if candidate_element == ec_element:
                            # Fill in action Cayley table value with the equivalence class label.
                            self.cayley_table_actions.iat[table_index_row, table_index_column] = labelling_element
                            is_filled_flag = True
                            break
                    if is_filled_flag:
                        break

                # If action Cayley table element (candidate_element) not in
                if not is_filled_flag:
                    equivalents_found = []
                    # Find state Cayley table row for element.
                    candidate_state_cayley_table_row = []
                    for labelling_element in self.cayley_table_states.index:
                        temp_action_sequence = labelling_element + candidate_element
                        candidate_state_cayley_table_row.append(
                            self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                  initial_agent_state=INITIAL_AGENT_STATE,
                                                  world=WORLD,
                                                  return_state_outcome=True))

                    # Find state Cayley table column for element.
                    candidate_state_cayley_table_column = []
                    for labelling_element in self.cayley_table_states.index:
                        temp_action_sequence = candidate_element + labelling_element
                        candidate_state_cayley_table_column.append(
                            self.findOutcomeAgent(action_sequence=temp_action_sequence,
                                                  initial_agent_state=INITIAL_AGENT_STATE,
                                                  world=WORLD,
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
                        # Fill in action Cayley table value with the equivalence class label.
                        self.cayley_table_actions.iat[table_index_row, table_index_column] = equivalents_found[0][0]
                        # Add equivalent to the relevant equivalence class.
                        self.ecs[equivalents_found[0][0]]['class_elements'].append(equivalents_found[0][1])
                    elif len(equivalents_found) > 1:
                        raise Exception('Too many equivalents: {0}'.format(equivalents_found))

        print('Cayley table generated.')
        pass

        # TODO: add each element to the Cayley table individually:
        #  1.-1. (DONE) Pop first element from cayley_table_candidate_elements.
        #  1.0. (DONE) Check element is not equivalent to other equivalent class labelling elements. If so, return to step -1.
        #  1.1. (DONE) Check element doesn't break equivalence classes --> if it does then split those equivalence classes.
        #  1.2. (DONE) Add element to Cayley tables, fill in its state Cayley table entries, and give it an equivalence class.
        #  1.3. (DONE) Iterate through state Cayley table and identify any new elements.
        #      a. If new element(s) found, then append them to cayley_table_candidate_elements.
        #  1.4. (DONE) Stop while loop when len(cayley_table_candidate_elements) == 0.
        #  2.0. (DONE) Go through equivalence classes and label them with the shortest labels.
        #  2.1. (DONE) Fill in action Cayley table entries.

    # TODO: checks:
    #  1. At end create new state Cayley table with the labelling rows and columns, then fill it in and compare to generated state Cayley table.    ---> This next. iterate through process, then set equivalence class labelling elements as minimum_actions, run again then check if two results are the same.
    #  2. (DONE) Look for equivalent elements in the state Cayley table.
    #  3. (DONE) Check that each element is present in only one equivalence class.
    #  4. Same algebra should be given for the same world if starting state is different.

    # TODO:
    #  1. Change sets to dictionaries with values as None to maintain ordering ?
    #  2. Improve variable names --> simiplify.
    #  3. Merge initial Cayley table filling into main Cayley table filling --> candidate elements = minimum action elements.

    def findOutcomeAgent(self, action_sequence, world, initial_agent_state, return_state_outcome=True):
        """
        #TODO: fix for return_state_outcome = False
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

    def findOutcomeCayley(self, left_action, right_action):
        """
        Uses the Cayley table to find the outcome of the action sequence: left_action \cdot right_action.

        :return: Outcome of left_action \cdot right_action.
        """
        if right_action not in self.cayley_table_actions.index:
            raise Exception('Right action ({0}) not in Cayley table.'.format(right_action))
        if left_action not in self.cayley_table_actions.columns:
            raise Exception('left action ({0}) not in Cayley table.'.format(left_action))

        outcome = self.cayley_table_actions.at[left_action, right_action]
        return outcome

    def saveCayleyTable(self, file_name):

        save_dict = {'cayley_table_states': self.cayley_table_states,
                     'cayley_table_actions': self.cayley_table_actions,
                     'equivalence_classes': self.ecs,
                     }

        path = './Saved Cayley tables'

        if not os.path.exists(path):
            os.makedirs('./Saved Cayley tables')

        with open(path + '/' + file_name, 'wb') as f:
            pickle.dump(save_dict, f, pickle.HIGHEST_PROTOCOL)

        print('\n Cayley table saved as: {0}'.format(file_name))

    def loadCayleyTable(self, file_name):

        path = './Saved Cayley tables'

        with open(path + '/' + file_name, 'rb') as f:
            save_dict = pickle.load(f)

        self.cayley_table_states = save_dict['cayley_table_states']
        self.cayley_table_actions = save_dict['cayley_table_actions']
        self.ecs = save_dict['equivalence_classes']

        self.name = file_name

#######################################################

if __name__ == "__main__":

    # print('\nNo walls')
    # table = CayleyTable()
    # parameters = {'minimum_actions': ['U', 'R', 'L', 'D', 'D', '1'],
    #               'initial_agent_state': (0, 0),
    #               'world': Gridworld2D(grid_size=(2, 2), wall_positions=[]),
    #               'show_calculation': False}  # TODO: remove from here and put in a print function. # TODO: Error when this is True.
    # table.generateCayleyTable(**parameters)
    # print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
    #                                                            len(table.cayley_table_states.columns.values)))
    # print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    # print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
    # print('\nEquivalence classes:')
    # for i in table.equivalence_classes.keys():
    #     print('    {0}:\t\t\t{1}'.format(i, table.equivalence_classes[i]))

    def runCode():
        print('\nWall at (0.5, 0)')
        table = CayleyTable()
        parameters = {'minimum_actions': ['U', 'R', 'L', 'D', 'D', '1'],
                      'initial_agent_state': (0, 0),
                      'world': Gridworld2D(grid_size=(2, 2), wall_positions=[(0.5, 0)]),
                      'show_calculation': False}  # TODO: remove from here and put in a print function. # TODO: Error when this is True.
        table.generate_cayley_table(**parameters)
        print('\nNo walls')
        print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                                   len(table.cayley_table_states.columns.values)))
        print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
        print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
        print('\nEquivalence classes:')
        for i in table.ecs.keys():
            print('    {0}:\t\t\t{1}'.format(i, table.ecs[i]))
        return table


    table1 = runCode()
    table1.saveCayleyTable(file_name='table')
    tables = [table1]

    # for t1 in tables:
    #     for t2 in tables:
    #         if (t1.cayley_table_actions.equals(t2.cayley_table_actions) == False) or (
    #                 t1.cayley_table_states.equals(t2.cayley_table_states) == False):
    #             raise Exception(
    #                 'Tables not equal:\nt1:\n{0}\nt2:\n{1}}'.format(t1.cayley_table_actions, t2.cayley_table_actions))