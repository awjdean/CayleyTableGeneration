"""
# TODO: error fix
    1. Check if error present after rolling back function addition in ~ line 515.
    2. No walls Cayley table now appears to be size 36 (2nd attempt gave size 29) instead of size 9 -  something has changed !





# TODO:
    1. Add self.table_ecs dictionary - equivalence class dictionary for Cayley tables elements only ?
        * Add self.table_ecs to load and save functions.
    2. Figure out why the Cayley table generating function is producing different results.
        2.1 Tests for Cayley table generating code.
        2.2 Find out if two Cayley tables are equivalent
            2.2.1 Does the Cayley table hold all the information of the transition algebra ?
            2.2.3 Can we reproduce the world from the Cayley table ?
    3. Replace sets with ordered sets.
    4. Improve efficiency of Cayley table generating code. --> NEXT.
        - Itertools instead of nested for loops --> more readable.
    5. Sort this error: D:\CodingProjects\PycharmProjects\WP1-CayleyTable\CayleyTable.py:471: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
  self.cayley_table_states[candidate_element] = candidate_state_cayley_table_column

# TODO (environments):
    1. Environment for masked actions being undefined.
    2. Environment for agent moving block in 1D.
    3. Environment for agent moving block in 2D.
    4. Plot gridworlds. --> NEXT.
        4.1 Plot the location of the agent in the world.

# TODO:
    1. Figure out
"""

from Environments.gridworld2D_walls import Gridworld2DWalls

# from numba import jit
import itertools
import copy
import pandas as pd
import os
import pickle
import time


########################################################################################################################
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


########################################################################################################################
def add_element_to_state_cayley_table(element,
                                      state_cayley_table,
                                      find_outcome_agent_function,
                                      outcome_agent_params,
                                      equivalence_classes=None):
    """
    :param element:
    :param state_cayley_table:
    :param find_outcome_agent_function:
    :param outcome_agent_params:
    :param equivalence_classes:
    :return:
    """
    _initial_agent_state = outcome_agent_params['initial_agent_state']
    _world = outcome_agent_params['world']

    # ------------------------------------------------------------------------------------------------------------------
    # TODO: change to function.

    # Find state Cayley table row for element ((column_label \circ a_{C}) * w_{0}).
    element_row = {}
    for column_label in state_cayley_table.columns:
        outcome = find_outcome_agent_function(action_sequence=(column_label + element),
                                              outcome_agent_params=outcome_agent_params)
        element_row[column_label] = outcome

    # Add candidate_element row to state Cayley table.
    element_row = pd.DataFrame([element_row],
                               columns=state_cayley_table.columns,
                               index=[element])
    state_cayley_table = pd.concat([state_cayley_table, element_row])

    # Find state Cayley table column for element ((a_{C} \circ row_label) * w_{0}).
    element_column = {}
    for row_label in state_cayley_table.index:
        outcome = find_outcome_agent_function(action_sequence=(element + row_label),
                                              outcome_agent_params=outcome_agent_params)
        element_column[row_label] = outcome

    # Add element column to state Cayley table.
    element_column = pd.Series(element_column,
                               name=element,
                               index=state_cayley_table.index)
    state_cayley_table = pd.concat([state_cayley_table, element_column],
                                   axis=1)

    # ------------------------------------------------------------------------------------------------------------------

    # TODO: SPLIT_FROM method:
    # SPLIT_FROM method - use split_from's column then complete. - will this work?
    # # Check this is the same as the row for split_from equivalence class.
    # if not temp_ec_label_state_cayley_table_column == self.cayley_table_states[
    #     temp_ecs[temp_ec_label]['split_from']].to_list():
    #     raise Exception('columns do not match')

    return state_cayley_table


########################################################################################################################
def find_outcome_agent(action_sequence, outcome_agent_params):
    """

    :param action_sequence:
    :param outcome_agent_params:
    :return:
    """

    # TODO: initialise world here to avoid vectorising issues?

    initial_agent_state = outcome_agent_params['initial_agent_state']
    world = outcome_agent_params['world']

    world.reset_agent_state(position=initial_agent_state)
    for action in action_sequence[::-1]:
        world.apply_minimum_agent_action(action=action)
    end_world_state = world.return_agent_position()

    return end_world_state


########################################################################################################################
def find_element_equivalents_in_state_cayley_table(element, state_cayley_table, outcome_agent_params):
    """
    Generates the state Cayley table row and column for the input element then
    :param element:
    :param state_cayley_table:
    :param outcome_agent_params:
    :return:
    """
    # TODO: docstring function.
    # TODO: improve efficiency of this.
    # 1. Convert to numpy and use matrix operations ?
    # 2. Store rows and columns for each matrix

    # ------------------------------------------------------------------------------------------------------------------
    # TODO: change to function - also used in add_element_to_cayley_table function

    # Find state Cayley table row for element ((column_label \circ element) * w_{0}).
    element_row = []
    for column_label in state_cayley_table.columns:
        outcome = find_outcome_agent(action_sequence=(column_label + element),
                                     outcome_agent_params=outcome_agent_params)
        element_row.append(outcome)

    # Find state Cayley table column for element ((element \circ row_label) * w_{0}).
    element_column = []
    for row_label in state_cayley_table.index:
        outcome = find_outcome_agent(action_sequence=(element + row_label),
                                     outcome_agent_params=outcome_agent_params)
        element_column.append(outcome)

    # ------------------------------------------------------------------------------------------------------------------

    # Compare row and column of this element to the rows and columns of the elements in the state Cayley table.
    equivalents_found = set()
    for cayley_element_index in range(len(state_cayley_table.index)):
        # TODO: check this
        cayley_element_row = list(state_cayley_table.iloc[cayley_element_index])
        cayley_element_column = list(state_cayley_table.iloc[:, cayley_element_index])

        if (cayley_element_row == element_row) and (cayley_element_column == element_column):
            equivalents_found.add((state_cayley_table.index[cayley_element_index], element))

    return equivalents_found


########################################################################################################################
def find_equivalents_in_state_cayley_table(state_cayley_table):
    """
    Finds elements in the state Cayley table that are equivalent to any of the other elements in the state Cayley
    table are equivalent.
    :param state_cayley_table:
    :return:
    """

    equivalents_found = {}
    for element_index in range(len(state_cayley_table.index)):
        if element_index in equivalents_found.keys():
            continue

        element_row = list(state_cayley_table.iloc[element_index])
        element_column = list(state_cayley_table.iloc[:, element_index])

        for comparison_element_index in range(len(state_cayley_table.index)):
            if (comparison_element_index == element_index) or (
                    comparison_element_index in equivalents_found.keys()):
                continue

            comparison_element_row = list(state_cayley_table.iloc[comparison_element_index])
            comparison_element_column = list(state_cayley_table.iloc[:, comparison_element_index])

            if (comparison_element_row == element_row) and (comparison_element_column == element_column):
                equivalents_found[comparison_element_index] = element_index

    return equivalents_found


########################################################################################################################

def find_broken_equivalence_classes(candidate_element, ecs, outcome_agent_params):
    temp_ecs = {}
    for ec_label in ecs.keys():

        # If equivalence class contains a single element, skip it because there are no equivalences to break.
        if len(ecs[ec_label]['class_elements']) == 1:
            continue

        # Find outcome of the equivalence class labelling element acting on w0 after the candidate element:
        # (ec_label \circ a_{C}) * w0.
        # TODO: do I already have this from the equivalence class check ?
        ec_label_outcome = find_outcome_agent(action_sequence=(ec_label + candidate_element),
                                              outcome_agent_params=outcome_agent_params)

        # Find outcome of each equivalence class element acting on w0 after the candidate element:
        # (ec_element \circ a_{C}) * w_{0}.
        # TODO: convert to list ?
        for ec_element in copy.deepcopy(ecs[ec_label]['class_elements']):
            ec_element_outcome = find_outcome_agent(action_sequence=(ec_element + candidate_element),
                                                    outcome_agent_params=outcome_agent_params)

            # If ec_element produces different result to the class_label_element, then need to split
            # ec_element into another equivalence class.
            if ec_label_outcome != ec_element_outcome:
                flag_temp_ec_found = False
                for temp_ec_label in temp_ecs.keys():
                    # To be in the same temporary equivalence class, elements must be split from the same
                    # equivalence class; therefore only check temporary equivalence classes split from
                    # ec_label's equivalence class.
                    if temp_ecs[temp_ec_label]['split_from'] != ec_label:
                        continue

                    # Find outcome of temp_ec_label acting on w0 after a_{C} has acted on w0
                    # (temp_ec_label \circ a_{C}) * w_{0}.
                    temp_ec_label_outcome = find_outcome_agent(
                        action_sequence=(temp_ec_label + candidate_element),
                        outcome_agent_params=outcome_agent_params)

                    # If the temp_ec_label_outcome is the same as the ec_element_outcome, then add ec_element
                    # to the temp_ec_label temporary equivalence class, and remove the ec_element from the
                    # ec_label equivalence class.
                    if ec_element_outcome == temp_ec_label_outcome:
                        # Add ec_element to temporary equivalence class
                        temp_ecs[temp_ec_label]['class_elements'].add(ec_element)
                        flag_temp_ec_found = True
                        # Remove ec_element from ec_label equivalence class.
                        ecs[ec_label]['class_elements'].remove(ec_element)
                        # Break from loop because each ec_element can only be in one temporary equivalence class.
                        break

                # If ec_element doesn't belong in any of the temporary equivalence classes, then create a new
                # temporary equivalence class for it.
                if not flag_temp_ec_found:
                    # Create new temporary equivalence class labelled by ec_element.
                    temp_ecs[ec_element] = {
                        'class_elements': set([ec_element]),
                        'end_world_state': ecs[ec_label]['end_world_state'],
                        'split_from': ec_label}
                    # Remove ec_element from ec_label equivalence class.
                    ecs[ec_label]['class_elements'].remove(ec_element)

    return temp_ecs, ecs


########################################################################################################################
class CayleyTable:
    INSTANCE_TYPE = 'CayleyTable'

    def __init__(self):

        self._cayley_table_parameters = None
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
            raise Exception('Cayley table already generated. World used: {0}'.format(self._cayley_table_parameters))

        # Unpack function arguments.
        _minimum_actions = parameters['minimum_actions']
        _outcome_agent_params = {'initial_agent_state': parameters['initial_agent_state'],
                                 'world': parameters['world'],
                                 }

        # Save Cayley table parameters.
        self._cayley_table_parameters = parameters

        remaining_minimum_actions = copy.deepcopy(_minimum_actions)  # TODO: remove ?
        visited_world_states = set()

        # Create equivalence classes dictionary.
        # Create dictionaries. Keys: actions labelling world states; Elements: actions that appear to be in the same
        # equivalence class (weak equivalence) as the key action.
        self.ecs = {}

        ################################################################################################################
        print('\nGenerating state Cayley table.')
        t_generate_cayleys = time.time()
        ################################################################################################################
        # PART I
        # Use minimum actions to create the initial state Cayley table using minimum actions, then fill the table.
        # TODO: Merge this into while loop:
        #   1. Create state Cayley table using first element in _minimum_actions.
        #   2. Add the minimum actions to candidate_cayley_elements.
        #   3. Start the while loop.
        #   - Could this method lead to a minimum action being removed too early, then never recovered ?
        ################################################################################################################
        # Create initial state Cayley table using minimum actions.
        ################################################################################################################
        self.cayley_table_states = pd.DataFrame(columns=copy.deepcopy(_minimum_actions),
                                                index=copy.deepcopy(_minimum_actions))

        ################################################################################################################
        # Fill initial state Cayley table.
        ################################################################################################################
        for row_index, column_index in itertools.product(range(len(self.cayley_table_states.index)),
                                                         range(len(self.cayley_table_states.columns))):
            right_action_sequence = self.cayley_table_states.index[row_index]
            left_action_sequence = self.cayley_table_states.columns[column_index]
            action_sequence = left_action_sequence + right_action_sequence

            outcome = find_outcome_agent(action_sequence=action_sequence,
                                         outcome_agent_params=_outcome_agent_params)

            # Fill state Cayley table.
            self.cayley_table_states.iat[row_index, column_index] = outcome

        ################################################################################################################
        # Create initial equivalence classes and remove equivalent elements from the state Cayley table.
        ################################################################################################################
        # Check if any of the elements in the state Cayley table are equivalent.
        equivalents_found = find_equivalents_in_state_cayley_table(state_cayley_table=self.cayley_table_states)

        # Create initial equivalence classes.
        rows_columns_to_keep = list(range(self.cayley_table_states.shape[0]))
        for i in range(len(self.cayley_table_states.index)):
            if i not in equivalents_found.keys():
                outcome = find_outcome_agent(action_sequence=_minimum_actions[i],
                                             outcome_agent_params=_outcome_agent_params)
                self.ecs[self.cayley_table_states.index[i]] = {
                    'class_elements': set([self.cayley_table_states.index[i]]),
                    'end_world_state': outcome,
                }
                visited_world_states.add(outcome)
            else:
                self.ecs[self.cayley_table_states.index[equivalents_found[i]]]['class_elements'].add(
                    self.cayley_table_states.index[i])
                rows_columns_to_keep.remove(i)

        # Remove equivalent elements from state Cayley table.
        self.cayley_table_states = self.cayley_table_states.iloc[rows_columns_to_keep, rows_columns_to_keep]

        ################################################################################################################
        # PART II
        # Identify newly discovered states in states Cayley table, and add equivalent states to the relevant
        # equivalence classes.
        ################################################################################################################
        # TODO: why do we need to check for equivalents here ?
        #  TODO: Surely just need to check if row and column elements are the same for each element here ==> check if this is true.
        #  TODO: is most (all?) of this an equivalents checking function ==> input: (element that we're checking equivalents for, Cayley table), return: (equivalents_found dictionary or tuple).
        ################################################################################################################
        candidate_cayley_table_elements = set()

        # TODO: change Cayley table fill to Cantor set covering method ?
        # Get the label for the candidate element using the row and column labelling elements from the state Cayley
        # table.
        for first_action_sequence, second_action_sequence in itertools.product(self.cayley_table_states.index,
                                                                               self.cayley_table_states.columns):
            candidate_element = second_action_sequence + first_action_sequence

            ############################################################################################################
            # Check if candidate element is equivalent to any of the elements in the Cayley table.
            ############################################################################################################
            # Search state Cayley table for elements that are equivalent to candidate_element.
            equivalents_found = find_element_equivalents_in_state_cayley_table(
                element=candidate_element,
                state_cayley_table=self.cayley_table_states,
                outcome_agent_params=_outcome_agent_params
            )

            if len(equivalents_found) == 0:
                # Add to new elements list
                candidate_cayley_table_elements.add(candidate_element)
            elif len(equivalents_found) == 1:
                # Add equivalent to the relevant equivalence class.
                equivalent = equivalents_found.pop()
                self.ecs[equivalent[0]]['class_elements'].add(equivalent[1])
            else:
                raise Exception('Too many equivalents: {0}'.format(equivalents_found))

        equivalents_found = None
        ################################################################################################################
        # PART III
        # Fill the state Cayley table.
        ################################################################################################################
        tx = time.time()
        while True:
            candidate_element = candidate_cayley_table_elements.pop()
            print(f'\tNum candidate_cayley_table_elements remaining: {len(candidate_cayley_table_elements)}')
            print(
                f'\t\t(Num state Cayley table elements, candidate, prev candidate time):\t({len(self.cayley_table_states.index)},\t{candidate_element},\t{round(time.time() - tx, 2)}s)')
            tx = time.time()

            ############################################################################################################
            # Check if candidate element is equivalent to another equivalent class labelling element.
            ############################################################################################################
            # Search state Cayley table for elements that are equivalent to candidate_element.
            equivalents_found = find_element_equivalents_in_state_cayley_table(
                element=candidate_element,
                state_cayley_table=self.cayley_table_states,
                outcome_agent_params=_outcome_agent_params
            )

            if len(equivalents_found) == 1:
                # Add equivalent to the relevant equivalence class, and move onto the next candidate element.
                equivalent = equivalents_found.pop()
                self.ecs[equivalent[0]]['class_elements'].add(equivalent[1])
                # continue            # TODO: this continue can lead to breaking form the while loop
            elif len(equivalents_found) > 1:
                raise Exception('Too many equivalents: {0}'.format(equivalents_found))

            equivalents_found = None
            ############################################################################################################
            # Check if the candidate element breaks equivalence classes. If so, then split those equivalence classes.
            ############################################################################################################
            #   To check if the candidate element breaks an equivalence class labelled by an element (l):
            #       1. Find the outcome of (l) \circ ( (c) * w0 ).
            #       2. For each equivalence class element (e), find the outcome of (e) \circ ( (c) * w0 ).
            #       3. If (l) \circ ( (c) * w0 ) != (e) \circ ( (c) * w0 ), then the candidate element breaks the
            #       equivalence class and equivalence class element (e) needs to be split into its own equivalence
            #       class.
            ############################################################################################################

            # TODO: sort this (after fixing while loop bug)
            # temp_ecs, self.ecs = find_broken_equivalence_classes(candidate_element=candidate_element,
            #                                                      ecs=self.ecs,
            #                                                      outcome_agent_params=_outcome_agent_params)

            temp_ecs = {}
            for ec_label in self.ecs.keys():

                # If equivalence class contains a single element, skip it because there are no equivalences to break.
                if len(self.ecs[ec_label]['class_elements']) == 1:
                    continue

                # Find outcome of the equivalence class labelling element acting on w0 after the candidate element:
                # (ec_label \circ a_{C}) * w0.
                # TODO: do I already have this from the equivalence class check ?
                ec_label_outcome = find_outcome_agent(action_sequence=(ec_label + candidate_element),
                                                      outcome_agent_params=_outcome_agent_params)

                # Find outcome of each equivalence class element acting on w0 after the candidate element:
                # (ec_element \circ a_{C}) * w_{0}.
                # TODO: convert to list ?
                for ec_element in copy.deepcopy(self.ecs[ec_label]['class_elements']):
                    ec_element_outcome = find_outcome_agent(action_sequence=(ec_element + candidate_element),
                                                            outcome_agent_params=_outcome_agent_params)

                    # If ec_element produces different result to the class_label_element, then need to split
                    # ec_element into another equivalence class.
                    if ec_label_outcome != ec_element_outcome:
                        flag_temp_ec_found = False
                        for temp_ec_label in temp_ecs.keys():
                            # To be in the same temporary equivalence class, elements must be split from the same
                            # equivalence class; therefore only check temporary equivalence classes split from
                            # ec_label's equivalence class.
                            if temp_ecs[temp_ec_label]['split_from'] != ec_label:
                                continue

                            # Find outcome of temp_ec_label acting on w0 after a_{C} has acted on w0
                            # (temp_ec_label \circ a_{C}) * w_{0}.
                            temp_ec_label_outcome = find_outcome_agent(
                                action_sequence=(temp_ec_label + candidate_element),
                                outcome_agent_params=_outcome_agent_params)

                            # If the temp_ec_label_outcome is the same as the ec_element_outcome, then add ec_element
                            # to the temp_ec_label temporary equivalence class, and remove the ec_element from the
                            # ec_label equivalence class.
                            if ec_element_outcome == temp_ec_label_outcome:
                                # Add ec_element to temporary equivalence class
                                temp_ecs[temp_ec_label]['class_elements'].add(ec_element)
                                flag_temp_ec_found = True
                                # Remove ec_element from ec_label equivalence class.
                                self.ecs[ec_label]['class_elements'].remove(ec_element)
                                # Break from loop because each ec_element can only be in one temporary equivalence class.
                                break

                        # If ec_element doesn't belong in any of the temporary equivalence classes, then create a new
                        # temporary equivalence class for it.
                        if not flag_temp_ec_found:
                            # Create new temporary equivalence class labelled by ec_element.
                            temp_ecs[ec_element] = {
                                'class_elements': set([ec_element]),
                                'end_world_state': self.ecs[ec_label]['end_world_state'],
                                'split_from': ec_label}
                            # Remove ec_element from ec_label equivalence class.
                            self.ecs[ec_label]['class_elements'].remove(ec_element)

            # ----------------------------------------------------------------------------------------------------------

            # TODO: happy with the above, but need to write up this part in Overleaf notes + split into a function.

            # TODO: work out theoretical maximum Cayley table size --> provides an error check.

            ############################################################################################################
            # Add broken equivalence classes to Cayley table and to main dictionary of equivalence classes.
            ############################################################################################################
            # TODO: SPLIT_FROM method: change so that this copies the rows and columns of the 'split_from' equivalence
            #  class ? --> remember to copy !
            for temp_ec_label in temp_ecs.keys():
                # Add temp_ec_label to state Cayley table.
                self.cayley_table_states = add_element_to_state_cayley_table(element=temp_ec_label,
                                                                             state_cayley_table=self.cayley_table_states,
                                                                             find_outcome_agent_function=find_outcome_agent,
                                                                             outcome_agent_params=_outcome_agent_params)

            # Merge temporary_equivalence classes into equivalence class dictionary.
            if len(temp_ecs.keys()) > 0:
                print(f'\tEquivalence class(es) split. Candidate element: {candidate_element}')
                print('\ttemp_ecs:')
                for j in temp_ecs.keys():
                    print(f'\t\t{temp_ecs[j]}')
            self.ecs = self.ecs | temp_ecs

            ############################################################################################################
            # Add candidate_element to the state Cayley table and to equivalence classes dictionary.
            ############################################################################################################
            # Add candidate element to state Cayley table.
            self.cayley_table_states = add_element_to_state_cayley_table(element=candidate_element,
                                                                         state_cayley_table=self.cayley_table_states,
                                                                         find_outcome_agent_function=find_outcome_agent,
                                                                         outcome_agent_params=_outcome_agent_params)

            # Create equivalence class for candidate element.
            self.ecs[candidate_element] = {'class_elements': set([candidate_element]),
                                           'end_world_state': find_outcome_agent(
                                               action_sequence=candidate_element,
                                               outcome_agent_params=_outcome_agent_params)
                                           }

            ############################################################################################################
            # Go through the state Cayley table and search for new elements
            # TODO: CHECKED UP TO HERE.

            # TODO: this is the same as when we went through the initial Cayley table. - start by making them consistent
            # TODO: this is a nasty brute force (entire) state Cayley method --> should be improved.

            # TODO: only activate if len(candidate_cayley_table_elements) == 0 ?
            # TODO: store
            # TODO: only need to go through rows and columns for newly added elements ? ==> have a new_cayley_elements list ?
            # TODO: break out if one new element is found ? - potentially reduces time checking equivalences of duplications? Would need to store where in the table we're got to --> Cantor covering method ?
            # TODO: Use Cantor covering method to get table indexes ?
            #
            # TODO: do I need to use this method to only check for new elements in the
            # for table_index_row in range(len(self.cayley_table_states.index)):
            #     for table_index_column in range(len(self.cayley_table_states.columns)):
            #         # Get labelling elements from Cayley table. # TODO: check this.
            #         right_action_sequence = self.cayley_table_states.index[
            #             table_index_row]  # TODO: ask Laure about this.
            #         left_action_sequence = self.cayley_table_states.columns[table_index_column]
            #         action_sequence = left_action_sequence + right_action_sequence

            ############################################################################################################

            # if len(candidate_cayley_table_elements) == 0:
            #     print(f'\n\tSearching for new candidate elements.')
            #     for row_index in range(len(self.cayley_table_states.index)):
            #         for column_index in range(len(self.cayley_table_states.columns)):
            #             # Get labelling elements from Cayley table. # TODO: check this.
            #             right_action_sequence = self.cayley_table_states.index[
            #                 row_index]  # TODO: ask Laure about this.
            #             left_action_sequence = self.cayley_table_states.columns[column_index]
            #             action_sequence = left_action_sequence + right_action_sequence
            #
            #             equivalents_found = find_element_equivalents_in_state_cayley_table(
            #                 element=action_sequence,
            #                 state_cayley_table=self.cayley_table_states,
            #                 outcome_agent_params=_outcome_agent_params)
            #
            #             if len(equivalents_found) == 0:
            #                 # Add to new elements list
            #                 candidate_cayley_table_elements.add(action_sequence)
            #             elif len(equivalents_found) == 1:
            #                 # Add equivalent to the relevant equivalence class
            #                 self.ecs[list(equivalents_found)[0][0]]['class_elements'].add(list(equivalents_found)[0][1])
            #             else:
            #                 raise Exception('Too many equivalents !')
            #     print(f'\t{len(candidate_cayley_table_elements)} candidate elements found.\n')

            self.searched_for_candidates = 0
            if len(candidate_cayley_table_elements) == 0:
                self.searched_for_candidates += 1
                print(f'\tSearching for new candidate elements.')
                for first_action_sequence, second_action_sequence in itertools.product(self.cayley_table_states.index,
                                                                                       self.cayley_table_states.columns):
                    action_sequence = second_action_sequence + first_action_sequence

                    equivalents_found = find_element_equivalents_in_state_cayley_table(
                        element=action_sequence,
                        state_cayley_table=self.cayley_table_states,
                        outcome_agent_params=_outcome_agent_params)

                    if len(equivalents_found) == 0:
                        # Add to new elements list
                        candidate_cayley_table_elements.add(action_sequence)
                    elif len(equivalents_found) == 1:
                        # Add equivalent to the relevant equivalence class
                        self.ecs[list(equivalents_found)[0][0]]['class_elements'].add(list(equivalents_found)[0][1])
                    else:
                        raise Exception('Too many equivalents !')
                print(f'\t{len(candidate_cayley_table_elements)} candidate elements found.')

            if len(candidate_cayley_table_elements) == 0:
                break

            ############################################################################################################
        print(f'candidate_cayley_table_elements: {candidate_cayley_table_elements}')
        print(f'State Cayley table generated (time taken: {round(time.time() - t_generate_cayleys, 2)}s).')
        ################################################################################################################
        # Part IV
        # Checks.
        ################################################################################################################
        print('\nPerforming checks.')
        tx = time.time()
        ################################################################################################################
        # CHECK for equivalent elements in the state Cayley table --> there should be none.
        ################################################################################################################
        equivalents_found = find_equivalents_in_state_cayley_table(state_cayley_table=self.cayley_table_states)

        if len(equivalents_found) > 0:
            raise Exception('Too many equivalents: {0}'.format(equivalents_found))

        ################################################################################################################
        # CHECK that each element is only in one equivalence class.
        ################################################################################################################

        ### Select element in equivalence class.
        for labelling_element in self.ecs.keys():
            for check_element in self.ecs[labelling_element]['class_elements']:
                ec_of_matching_elements = []
                ### Check if element is the same as any of the other elements in this equivalence class.
                for comparison_element in self.ecs[labelling_element]['class_elements']:
                    if check_element == comparison_element:
                        ec_of_matching_elements.append(labelling_element)

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

        print(f'Checks complete (time taken: {round(time.time() - tx, 2)}s).')
        ################################################################################################################
        # Part V
        # Action Cayley table.
        ################################################################################################################
        print('\nGenerating action Cayley table.')
        tx = time.time()
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

        # ################################################################################################################
        # # Create and fill action Cayley table.
        # ################################################################################################################
        #
        # # create action Cayley table.
        # self.cayley_table_actions = pd.DataFrame(columns=self.cayley_table_states.columns,
        #                                          index=self.cayley_table_states.index)
        # self.cayley_table_ecs = {}
        #
        # # Fill action Cayley table.
        # for row_index in range(len(self.cayley_table_actions.index)):
        #     for column_index in range(len(self.cayley_table_actions.columns)):
        #         is_filled_flag = False
        #         # Get labelling elements from Cayley table.
        #         right_action_sequence = self.cayley_table_states.index[row_index]  # TODO: ask Laure about this.
        #         left_action_sequence = self.cayley_table_states.columns[column_index]
        #         candidate_element = left_action_sequence + right_action_sequence
        #
        #         # Find label of equivalence class containing action_sequence, then use that label in the actions Cayley table.
        #         for labelling_element in self.ecs.keys():
        #             for ec_element in self.ecs[labelling_element]['class_elements']:
        #                 if candidate_element == ec_element:
        #                     # Fill in action Cayley table value with the equivalence class label.
        #                     self.cayley_table_actions.iat[row_index, column_index] = labelling_element
        #                     is_filled_flag = True
        #                     break
        #             if is_filled_flag:
        #                 break
        #
        #         # If action Cayley table element (candidate_element) not in
        #         if not is_filled_flag:
        #             # --------------------------------------------------------------------------------------------------
        #             # TODO: This looks like find_element_equivalents_in_state_cayley_table function.
        #
        #             equivalents_found = []
        #             # Find state Cayley table row for element.
        #             candidate_state_cayley_table_row = []
        #             for labelling_element in self.cayley_table_states.index:
        #                 temp_action_sequence = labelling_element + candidate_element
        #                 candidate_state_cayley_table_row.append(
        #                     find_outcome_agent(action_sequence=temp_action_sequence,
        #                                        outcome_agent_params=_outcome_agent_params))
        #
        #             # Find state Cayley table column for element.
        #             candidate_state_cayley_table_column = []
        #             for labelling_element in self.cayley_table_states.index:
        #                 temp_action_sequence = candidate_element + labelling_element
        #                 candidate_state_cayley_table_column.append(
        #                     find_outcome_agent(action_sequence=temp_action_sequence,
        #                                        outcome_agent_params=_outcome_agent_params))
        #
        #             # Compare row ond column of this element to the rows and columns of the elements in the state Cayley table.
        #             for comparison_element_index in range(len(self.cayley_table_states.index)):
        #                 comparison_element_row = list(self.cayley_table_states.iloc[comparison_element_index])
        #                 comparison_element_column = list(self.cayley_table_states.iloc[:, comparison_element_index])
        #
        #                 if (comparison_element_row == candidate_state_cayley_table_row) and (
        #                         comparison_element_column == candidate_state_cayley_table_column):
        #                     equivalents_found.append(
        #                         (self.cayley_table_states.index[comparison_element_index], candidate_element))
        #
        #             # --------------------------------------------------------------------------------------------------
        #
        #             if len(equivalents_found) == 1:
        #                 # Fill in action Cayley table value with the equivalence class label.
        #                 self.cayley_table_actions.iat[row_index, column_index] = equivalents_found[0][0]
        #                 # Add equivalent to the relevant equivalence class.
        #                 self.ecs[equivalents_found[0][0]]['class_elements'].append(equivalents_found[0][1])
        #             elif len(equivalents_found) > 1:
        #                 raise Exception('Too many equivalents: {0}'.format(equivalents_found))
        #
        # print(f'Action Cayley table generated (time taken: {round(time.time() - tx, 2)}s).')

        # TODO: add each element to the Cayley table individually:
        #  1.-1. (DONE) Pop first element from candidate_cayley_table_elements.
        #  1.0. (DONE) Check element is not equivalent to other equivalent class labelling elements. If so, return to step -1.
        #  1.1. (DONE) Check element doesn't break equivalence classes --> if it does then split those equivalence classes.
        #  1.2. (DONE) Add element to Cayley tables, fill in its state Cayley table entries, and give it an equivalence class.
        #  1.3. (DONE) Iterate through state Cayley table and identify any new elements.
        #      a. If new element(s) found, then append them to candidate_cayley_table_elements.
        #  1.4. (DONE) Stop while loop when len(candidate_cayley_table_elements) == 0.
        #  2.0. (DONE) Go through equivalence classes and label them with the shortest labels.
        #  2.1. (DONE) Fill in action Cayley table entries.

    # TODO: checks:
    #  1. At end create new state Cayley table with the labelling rows and columns, then fill it in and compare to generated state Cayley table.    ---> This next. iterate through process, then set equivalence class labelling elements as minimum_actions, run again then check if two results are the same.
    #  2. (DONE) Look for equivalent elements in the state Cayley table.
    #  3. (DONE) Check that each element is present in only one equivalence class.
    #  4. Same algebra should be given for the same world if starting state is different.

    # TODO:
    #  1. Change sets to dictionaries with values as None to maintain ordering ?
    #  2. Improve variable names --> simplify.
    #  3. Merge initial Cayley table filling into main Cayley table filling --> candidate elements = minimum action elements.

    def find_outcome_cayley(self, left_action, right_action):
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

    def save_cayley_table(self, file_name):

        save_dict = {'cayley_table_states': self.cayley_table_states,
                     'cayley_table_actions': self.cayley_table_actions,
                     'equivalence_classes': self.ecs,
                     'cayley_table_parameters': self._cayley_table_parameters,
                     }
        path = './Saved Cayley tables/'

        if not os.path.exists(path):
            os.makedirs('./Saved Cayley tables/')

        with open(path + file_name, 'wb') as f:
            pickle.dump(save_dict, f, pickle.HIGHEST_PROTOCOL)

        print('\n Cayley table saved as: {0}'.format(file_name))

    def load_cayley_table(self, file_name):

        path = './Saved Cayley tables/'
        with open(path + file_name, 'rb') as f:
            save_dict = pickle.load(f)

        self.cayley_table_states = save_dict['cayley_table_states']
        self.cayley_table_actions = save_dict['cayley_table_actions']
        self.ecs = save_dict['equivalence_classes']
        self._cayley_table_parameters = save_dict['cayley_table_parameters']

        self.name = file_name


#######################################################
if __name__ == "__main__":
    grid_size = (2, 2)
    wall_positions = [(1, 0.5), (1.5, 1)]
    initial_agent_state = (0, 0)
    minimum_actions = ['U', 'R', 'L', 'D', 'D', '1']

    t0 = time.time()
    print('\nNo walls')
    table = CayleyTable()
    parameters = {'minimum_actions': minimum_actions,
                  'initial_agent_state': initial_agent_state,
                  'world': Gridworld2DWalls(grid_size=grid_size, wall_positions=[]),
                  }
    table.generate_cayley_table(**parameters)
    print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                               len(table.cayley_table_states.columns.values)))
    print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
    print('\nEquivalence classes:')
    for i in table.ecs.keys():
        print('    {0}:\t\t\t{1}'.format(i, table.ecs[i]))
    table.save_cayley_table(file_name=f'table_{grid_size[0]}x{grid_size[1]}_no_walls_s4')
    print(f'\nTotal time taken: {round(time.time() - t0, 2)}s')

    t0 = time.time()
    print('\nWall at (0.5, 0)')
    table = CayleyTable()
    parameters = {'minimum_actions': minimum_actions,
                  'initial_agent_state': initial_agent_state,
                  'world': Gridworld2DWalls(grid_size=grid_size, wall_positions=wall_positions),
                  }
    table.generate_cayley_table(**parameters)
    print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                               len(table.cayley_table_states.columns.values)))
    print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
    print('\nEquivalence classes:')
    for i in table.ecs.keys():
        print('\t{0}:\t\t\t{1}'.format(i, table.ecs[i]))
    file_name = f'table_{grid_size[0]}x{grid_size[1]}_wall_{str(wall_positions).replace(", ", "_")}_identity_s4'
    table.save_cayley_table(file_name=file_name)
    print(f'\nTotal time taken: {round(time.time() - t0, 2)}s')
