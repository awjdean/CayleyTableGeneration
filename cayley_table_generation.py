import time
import itertools
import pandas
import copy
import concurrent.futures

########################################################################################################################
"""
# TODO order:
    - Make it so you don't have to recheck parts of the state Cayley table for new elements - input the previously checked row/column index and adjust range to start from there +1
    - Efficiency 0.

# TODO (issues):
    1. Issues with different Cayley tables being produced - need way to check the equivalence of the tables.

# TODO (general):
    1. Logging instead of printing (?).
    3. Add self.table_ecs dictionary - equivalence class dictionary for Cayley tables elements only ?
        - Add self.table_ecs to load and save functions.
    4. Merge initial Cayley table filling into main Cayley table filling (while loop)
        - candidate elements = minimum action elements?
    5. Write up find_broken_equivalence_classes in Overleaf notes.

# TODO (theory):
    1. Work out theoretical maximum Cayley table size for 2D gridworlds --> provides an error check.

# TODO (improving efficiency):
    0. Use dictionaries instead of Pandas dataframes, then put final result into Pandas dataframe.
    2. Test parallelisation to find out which method is better.
        - Set to use all available cores.
    3. Only check for elements in part of the Cayley table where elements haven't already been checked for.
    4. Parallelise find_broken_equivalence_classes function.
    5. Implement split_form method for find_broken_equivalence_classes function (?).

# TODO (checks):
    2. At end create new state Cayley table with the labelling rows and columns, then fill it in and compare to generated state Cayley table.
        - Iterate through process, then set equivalence class labelling elements as minimum_actions, run again then check if two results are the same.
    3. Should be able to move from one algebra to another with a different initial state by applying the relevant operation to every element in the Cayley table

# TODO (additional functionality):
    2. Find out if two Cayley tables are equivalent
    3. Reproducing world structure from Cayley table.
        - Does the Cayley table hold all the information of the transition algebra ?
    4. Function to generate Cayley table from different initial position using a previously generated Cayley table.

# TODO (environments):
    4. 3D gridworld.
    5. Graph world.
    6. Different minimum actions (rotate 90 degrees + move forwards).
    7. Hexagonal world.
"""


########################################################################################################################
def generate_cayley_table(cayley_table, minimum_actions: list, world):
    """
    # TODO: have generate_cayley_table as function separate from CayleyTable class, then:
        * Put all the properties stuff as functions of that class.
        * Have a to_pandas_dataframe class.

    :return:
    """

    # Save Cayley table generation parameters.
    cayley_table.cayley_table_generation_parameters = {'minimum_actions': minimum_actions,
                                                       'world': world
                                                       }

    # TODO: remove ?
    visited_world_states = set()

    # Create equivalence classes dictionary.
    # Create dictionaries. Keys: actions labelling world states; Elements: actions that appear to be in the same
    # equivalence class (weak equivalence) as the key action.
    cayley_table.ecs = {}

    ################################################################################################################
    print('\nGenerating state Cayley table.')
    t_generate_cayleys = time.time()
    ################################################################################################################
    # PART I - # TODO: put into function - generate_initial_state_cayley_table
    # Use minimum actions to create the initial state Cayley table using minimum actions, then fill the table.
    # TODO: Merge this into while loop(?):
    #   1. Create state Cayley table using first element in _minimum_actions.
    #   2. Add the minimum actions to candidate_cayley_elements.
    #   3. Start the while loop.
    #   - Could this method lead to a minimum action being removed too early, then never recovered ?
    ################################################################################################################
    # Create initial state Cayley table using minimum actions.
    ################################################################################################################
    # TODO: pandas --> dict?
    cayley_table.cayley_table_states = pandas.DataFrame(columns=copy.deepcopy(minimum_actions),
                                                        index=copy.deepcopy(minimum_actions))

    ################################################################################################################
    # Fill initial state Cayley table.
    ################################################################################################################
    for row_index, column_index in itertools.product(range(len(cayley_table.cayley_table_states.index)),
                                                     range(len(cayley_table.cayley_table_states.columns))):
        right_action_sequence = cayley_table.cayley_table_states.index[row_index]
        left_action_sequence = cayley_table.cayley_table_states.columns[column_index]
        action_sequence = left_action_sequence + right_action_sequence

        outcome = find_outcome_agent(action_sequence=action_sequence,
                                     world=world)

        # Fill state Cayley table.
        cayley_table.cayley_table_states.iat[row_index, column_index] = outcome

    ################################################################################################################
    # Create initial equivalence classes and remove equivalent elements from the state Cayley table.
    ################################################################################################################
    # Check if any of the elements in the state Cayley table are equivalent.
    equivalents_found = find_equivalents_in_state_cayley_table(state_cayley_table=cayley_table.cayley_table_states)

    # Create initial equivalence classes.
    rows_columns_to_keep = list(range(cayley_table.cayley_table_states.shape[0]))
    for i in range(len(cayley_table.cayley_table_states.index)):
        if i not in equivalents_found.keys():
            outcome = find_outcome_agent(action_sequence=minimum_actions[i],
                                         world=world)
            cayley_table.ecs[cayley_table.cayley_table_states.index[i]] = {
                'class_elements': set([cayley_table.cayley_table_states.index[i]]),
                'end_world_state': outcome,
            }
            visited_world_states.add(outcome)
        else:
            cayley_table.ecs[cayley_table.cayley_table_states.index[equivalents_found[i]]]['class_elements'].add(
                cayley_table.cayley_table_states.index[i])
            rows_columns_to_keep.remove(i)

    # Remove equivalent elements from state Cayley table.
    cayley_table.cayley_table_states = cayley_table.cayley_table_states.iloc[rows_columns_to_keep, rows_columns_to_keep]

    ################################################################################################################
    # PART II
    # Fill the state Cayley table.
    ################################################################################################################
    tx = time.time()
    candidate_cayley_table_elements = set()
    while True:
        ############################################################################################################
        # Go through the state Cayley table and search for new elements
        ############################################################################################################
        # TODO: this is the same as when we went through the initial Cayley table. - start by making them consistent
        # TODO: this is a nasty brute force (entire) state Cayley method --> should be improved.
        # TODO: only need to go through rows and columns for newly added elements ? ==> have a new_cayley_elements list ?
        # TODO: break out if one new element is found ? - potentially reduces time checking equivalences of duplications? Would need to store where in the table we're got to --> Cantor covering method ?
        # TODO: Use Cantor covering method to get table indexes ?
        ############################################################################################################
        if len(candidate_cayley_table_elements) == 0:
            tx2 = time.time()
            candidate_cayley_table_elements = search_state_cayley_table_for_new_candidate_elements(
                cayley_table_states=cayley_table.cayley_table_states,
                world=world,
                equivalence_classes=cayley_table.ecs)
            print(
                f'\t{len(candidate_cayley_table_elements)} candidate elements found (time taken: {round(time.time() - tx2, 2)}s).')

        ############################################################################################################
        # If there are no candidate elements then the state Cayley table is complete.
        ############################################################################################################
        if len(candidate_cayley_table_elements) == 0:
            break

        # Select candidate_element.
        candidate_element = candidate_cayley_table_elements.pop()
        print(f'\tNum candidate_cayley_table_elements remaining: {len(candidate_cayley_table_elements)}')
        print(
            f'\t\t(Num state Cayley table elements, candidate, prev candidate time):\t({len(cayley_table.cayley_table_states.index)},\t{candidate_element},\t{round(time.time() - tx, 2)}s)')
        tx = time.time()
        ############################################################################################################
        # Check if candidate element is equivalent to another equivalent class labelling element.
        ############################################################################################################
        # Search state Cayley table for elements that are equivalent to candidate_element.
        equivalents_found = find_element_equivalents_in_state_cayley_table(
            element=candidate_element,
            state_cayley_table=cayley_table.cayley_table_states,
            world=world)

        if len(equivalents_found) == 1:
            # Add equivalent to the relevant equivalence class, and move onto the next candidate element.
            equivalent = equivalents_found.pop()
            cayley_table.ecs[equivalent[0]]['class_elements'].add(equivalent[1])
            continue
        elif len(equivalents_found) > 1:
            raise Exception('Too many equivalents: {0}'.format(equivalents_found))

        ############################################################################################################
        # Check if the candidate element breaks equivalence classes. If so, then split those equivalence classes.
        ############################################################################################################
        temp_ecs, cayley_table.ecs = find_broken_equivalence_classes(candidate_element=candidate_element,
                                                                     ecs=cayley_table.ecs,
                                                                     world=world)

        ############################################################################################################
        # Add broken equivalence classes to Cayley table and to main dictionary of equivalence classes.
        ############################################################################################################
        # TODO: SPLIT_FROM method: change so that this copies the rows and columns of the 'split_from' equivalence
        #  class ? --> remember to copy !
        for temp_ec_label in temp_ecs.keys():
            # Add temp_ec_label to state Cayley table.
            cayley_table.cayley_table_states = add_element_to_state_cayley_table(element=temp_ec_label,
                                                                                 state_cayley_table=cayley_table.cayley_table_states,
                                                                                 world=world)

        # Merge temporary_equivalence classes into equivalence class dictionary.
        if len(temp_ecs.keys()) > 0:
            print(f'\tEquivalence class(es) split. Candidate element: {candidate_element}')
            print('\t\ttemp_ecs:')
            for j in temp_ecs.keys():
                print(f'\t\t{temp_ecs[j]}')
        cayley_table.ecs = cayley_table.ecs | temp_ecs

        ############################################################################################################
        # Add candidate_element to the state Cayley table and to equivalence classes dictionary.
        ############################################################################################################
        # Add candidate element to state Cayley table.
        cayley_table.cayley_table_states = add_element_to_state_cayley_table(element=candidate_element,
                                                                             state_cayley_table=cayley_table.cayley_table_states,
                                                                             world=world)

        # Create equivalence class for candidate element.
        cayley_table.ecs[candidate_element] = {'class_elements': set([candidate_element]),
                                               'end_world_state': find_outcome_agent(
                                                   action_sequence=candidate_element,
                                                   world=world)
                                               }

        ############################################################################################################
    print(f'State Cayley table generated (time taken: {round(time.time() - t_generate_cayleys, 2)}s).')
    ################################################################################################################
    # Part III
    # Checks.
    ################################################################################################################
    print('\nPerforming checks.')
    tx = time.time()
    ################################################################################################################
    # CHECK for equivalent elements in the state Cayley table --> there should be none.
    ################################################################################################################
    try:
        assert len(find_equivalents_in_state_cayley_table(state_cayley_table=cayley_table.cayley_table_states)) == 0
    except AssertionError:
        raise Exception(
            f"Too many equivalents: {find_equivalents_in_state_cayley_table(state_cayley_table=cayley_table.cayley_table_states)}")

    ################################################################################################################
    # CHECK that each element is only in one equivalence class.
    ################################################################################################################
    check_each_action_sequence_in_single_equivalence_class(equivalence_classes=cayley_table.ecs)

    print(f'Checks complete (time taken: {round(time.time() - tx, 2)}s).')

    ################################################################################################################
    # Part IV
    # Action Cayley table.
    ################################################################################################################
    print('\nGenerating action Cayley table.')
    tx = time.time()

    # Relabel equivalence classes with their shortest label and change the relevant Cayley table row-column labels.
    cayley_table.ecs, cayley_table.cayley_table_states = relabel_equivalence_classes(
        equivalence_classes=cayley_table.ecs,
        cayley_table_states=cayley_table.cayley_table_states)

    # Create and fill action Cayley table.
    cayley_table.cayley_table_actions, cayley_table.ecs = generate_action_cayley_table(
        equivalence_classes=cayley_table.ecs,
        cayley_table_states=cayley_table.cayley_table_states,
        world=world)

    # Generate equivalence for action Cayley table elements only.
    cayley_table.cayley_table_ecs = generate_action_cayley_equivalence_classes(equivalence_classes=cayley_table.ecs,
                                                                               cayley_table_actions=cayley_table.cayley_table_actions,
                                                                               cayley_table_states=cayley_table.cayley_table_states)

    # Check there are no NaNs in action Cayley table.
    try:
        assert not check_dataframe_for_nans(dataframe=cayley_table.cayley_table_actions)
    except AssertionError:
        raise Exception(f"NaNs found in action Cayley table:\n{cayley_table.cayley_table_states.to_string()}")

    print(f'Action Cayley table generated (time taken: {round(time.time() - tx, 2)}s).')


########################################################################################################################
def search_state_cayley_table_for_new_candidate_elements(cayley_table_states, world, equivalence_classes):
    """
    Search state Cayley table for new candidate elements.
    """
    print(f'\tSearching for new candidate elements.')
    candidate_cayley_table_elements = set()
    for first_action_sequence, second_action_sequence in itertools.product(cayley_table_states.index,
                                                                           cayley_table_states.columns):
        candidate_element = second_action_sequence + first_action_sequence

        equivalents_found = find_element_equivalents_in_state_cayley_table(element=candidate_element,
                                                                           state_cayley_table=cayley_table_states,
                                                                           world=world)

        if len(equivalents_found) == 0:
            # Add to new elements list.
            candidate_cayley_table_elements.add(candidate_element)
        elif len(equivalents_found) == 1:
            # Add equivalent to the relevant equivalence class.
            equivalent = equivalents_found.pop()
            equivalence_classes[equivalent[0]]['class_elements'].add(equivalent[1])
        else:
            raise Exception('Too many equivalents !')

    return candidate_cayley_table_elements


########################################################################################################################
def check_dataframe_for_nans(dataframe):
    """
    Checks pandas dataframe for NaNs. Returns True if NaN found, else returns False.
    """
    nan_values = dataframe.isna()

    for row_index, column_index in itertools.product(range(len(nan_values.index)), range(len(nan_values.columns))):
        if nan_values.iat[row_index, column_index]:
            return True
    return False


########################################################################################################################
def generate_action_cayley_equivalence_classes(equivalence_classes, cayley_table_actions, cayley_table_states):
    """
    Generate equivalence for action Cayley table elements only.
    """
    cayley_table_ecs = {}

    # Create equivalence classes.
    for labelling_element in equivalence_classes.keys():
        cayley_table_ecs[labelling_element] = {'class_elements': [labelling_element],
                                               'end_world_state': equivalence_classes[labelling_element][
                                                   'end_world_state']}

    for row_index, column_index in itertools.product(range(len(cayley_table_actions.index)),
                                                     range(len(cayley_table_actions.columns))):
        is_filled_flag = False
        # Get labelling elements from Cayley table.
        right_action_sequence = cayley_table_states.index[row_index]
        left_action_sequence = cayley_table_states.columns[column_index]
        candidate_element = left_action_sequence + right_action_sequence

        # Find label of equivalence class containing action_sequence, then use that label in the actions Cayley
        # table.
        for labelling_element in equivalence_classes.keys():
            for ec_element in equivalence_classes[labelling_element]['class_elements']:
                if candidate_element == ec_element:
                    # Add ec_element to the equivalence class labelled by labelling_element.
                    cayley_table_ecs[labelling_element]['class_elements'].append(candidate_element)
                    is_filled_flag = True
                    break
            if is_filled_flag:
                break

    return cayley_table_ecs


########################################################################################################################
def generate_action_cayley_table(equivalence_classes, cayley_table_states, world):
    """
    Create and fill action Cayley table.
    """
    # create action Cayley table.
    cayley_table_actions = pandas.DataFrame(columns=cayley_table_states.columns,
                                            index=cayley_table_states.index)

    # Fill action Cayley table.
    for row_index, column_index in itertools.product(range(len(cayley_table_actions.index)),
                                                     range(len(cayley_table_actions.columns))):
        is_filled_flag = False
        # Get labelling elements from Cayley table.
        right_action_sequence = cayley_table_states.index[row_index]
        left_action_sequence = cayley_table_states.columns[column_index]
        candidate_element = left_action_sequence + right_action_sequence

        # Find label of equivalence class containing action_sequence, then use that label in the actions Cayley
        # table.
        for labelling_element in equivalence_classes.keys():
            for ec_element in equivalence_classes[labelling_element]['class_elements']:
                if candidate_element == ec_element:
                    # Fill in action Cayley table value with the equivalence class label.
                    cayley_table_actions.iat[row_index, column_index] = labelling_element
                    is_filled_flag = True
                    break
            if is_filled_flag:
                break

        # If action Cayley table element (candidate_element) not a member of an equivalence class, then find its
        # equivalent in the state Cayley table.
        if not is_filled_flag:
            equivalents_found = find_element_equivalents_in_state_cayley_table(element=candidate_element,
                                                                               state_cayley_table=cayley_table_states,
                                                                               world=world)
            if len(equivalents_found) == 1:
                # Fill in action Cayley table value with the equivalence class label.
                cayley_table_actions.iat[row_index, column_index] = list(equivalents_found)[0][0]
                # Add equivalent to the relevant equivalence class.
                equivalence_classes[list(equivalents_found)[0][0]]['class_elements'].append(
                    list(equivalents_found)[0][1])
            elif len(equivalents_found) > 1:
                raise Exception('Too many equivalents: {0}'.format(equivalents_found))

    return cayley_table_actions, equivalence_classes


########################################################################################################################
def relabel_equivalence_classes(equivalence_classes, cayley_table_states):
    """
    Relabel equivalence classes with the shortest minimum action sequence, then alphabetically.
    """
    cayley_table_relabelling_dict = {}
    old_ec_labels = list(equivalence_classes.keys())
    for ec_label in old_ec_labels:
        # Sort equivalence class elements by alphabetical order and length order.
        sorted_ec_elements = sorted(list(equivalence_classes[ec_label]['class_elements']))
        sorted_ec_elements = sorted(sorted_ec_elements, key=len)

        # New labelling element is first element in sorted_ec_elements.
        new_ec_label = sorted_ec_elements[0]

        # Store relabelling.
        cayley_table_relabelling_dict[ec_label] = new_ec_label

        # Relabel equivalence class.
        equivalence_classes[new_ec_label] = equivalence_classes.pop(ec_label)
        equivalence_classes[new_ec_label]['class_elements'] = sorted_ec_elements

    # Relabel state Cayley table.
    cayley_table_states = cayley_table_states.rename(columns=cayley_table_relabelling_dict,
                                                     index=cayley_table_relabelling_dict)

    # TODO: do this when generating pandas dataframe from dictionary?
    # Order state Cayley table rows and columns according to same ordering as equivalence classes were relabeled.
    cayley_tables_row_columns = list(cayley_table_states.index)
    sorted_cayley_tables_row_columns = sorted(cayley_tables_row_columns)
    sorted_cayley_tables_row_columns = sorted(sorted_cayley_tables_row_columns, key=len)
    cayley_table_states = cayley_table_states.reindex(index=sorted_cayley_tables_row_columns,
                                                      columns=sorted_cayley_tables_row_columns)

    return equivalence_classes, cayley_table_states


########################################################################################################################
def generate_state_cayley_row(element, state_cayley_table, world):
    # TODO: parallelise this.
    """
    Generates state Cayley table row for element ((column_label \circ a_{C}) * w_{0}).
    :param world:
    :param element:
    :param state_cayley_table:
    :return:
    """
    # # New method.
    # element_row = {}
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     # Use map() to apply find_outcome_agent() to each column label in parallel
    #     result = {executor.submit(find_outcome_agent,
    #                               column_label + element,
    #                               copy.deepcopy(world)): column_label for column_label in state_cayley_table.columns}
    #     for future in concurrent.futures.as_completed(result):
    #         column_label = result[future]
    #         outcome = future.result()
    #         element_row[column_label] = outcome

    # Old method.
    element_row2 = {}
    for column_label2 in state_cayley_table.columns:
        outcome = find_outcome_agent(action_sequence=(column_label2 + element),
                                     world=world)  # TODO: have removed deepcopy.
        element_row2[column_label2] = outcome
    element_row = element_row2
    # Check if new method gives same result as old method.
    # if element_row != element_row2:
    #     raise Exception(f"element_column != element_column2: \n{element_row}, \n{element_row2}")

    return element_row


########################################################################################################################
def generate_state_cayley_column(element, state_cayley_table, world):
    # TODO: parallelise this.
    """
    Generates state Cayley table column for element ((a_{C} \circ row_label) * w_{0}).
    :param element:
    :param state_cayley_table:
    :param world:
    :return:
    """
    # # New method.
    # element_column = {}
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     # Use map() to apply find_outcome_agent() to each row label in parallel
    #     result = {executor.submit(find_outcome_agent,
    #                               element + row_label,
    #                               copy.deepcopy(world)): row_label for row_label in state_cayley_table.index}
    #     for future in concurrent.futures.as_completed(result):
    #         row_label = result[future]
    #         outcome = future.result()
    #         element_column[row_label] = outcome

    # Old method.
    element_column2 = {}
    for row_label2 in state_cayley_table.index:
        outcome = find_outcome_agent(action_sequence=(element + row_label2),
                                     world=world)  # TODO: have removed deepcopy.
        element_column2[row_label2] = outcome
    element_column = element_column2
    # # Check if new method gives same result as old method.
    # if element_column != element_column2:
    #     raise Exception(f"element_column != element_column2: \n{element_column}, \n{element_column2}")

    return element_column


########################################################################################################################
def add_element_to_state_cayley_table(element,
                                      state_cayley_table,
                                      world,
                                      equivalence_classes=None):
    """
    Adds an element to the state Cayley table and fills in the row and column for that element.
    :param world:
    :param element:
    :param state_cayley_table:
    :param equivalence_classes:
    :return:
    """
    # Generate state Cayley table row for element.
    element_row = generate_state_cayley_row(element=element,
                                            state_cayley_table=state_cayley_table,
                                            world=world)
    # Add candidate_element row to state Cayley table.
    element_row = pandas.DataFrame([element_row],
                                   columns=state_cayley_table.columns,
                                   index=[element])
    state_cayley_table = pandas.concat([state_cayley_table, element_row])

    # Generate state Cayley table column for element.
    element_column = generate_state_cayley_column(element=element,
                                                  state_cayley_table=state_cayley_table,
                                                  world=world)
    # Add element column to state Cayley table.
    element_column = pandas.Series(element_column,
                                   name=element,
                                   index=state_cayley_table.index)
    state_cayley_table = pandas.concat([state_cayley_table, element_column],
                                       axis=1)

    # TODO: SPLIT_FROM method:
    # SPLIT_FROM method - use split_from's column then complete. - will this work?
    # # Check this is the same as the row for split_from equivalence class.
    # if not temp_ec_label_state_cayley_table_column == self.cayley_table_states[
    #     temp_ecs[temp_ec_label]['split_from']].to_list():
    #     raise Exception('columns do not match')

    return state_cayley_table


########################################################################################################################
def check_each_action_sequence_in_single_equivalence_class(equivalence_classes):
    ### Select element in equivalence class.
    for labelling_element in equivalence_classes.keys():
        for check_element in equivalence_classes[labelling_element]['class_elements']:
            ec_of_matching_elements = []
            ### Check if element is the same as any of the other elements in this equivalence class.
            for comparison_element in equivalence_classes[labelling_element]['class_elements']:
                if check_element == comparison_element:
                    ec_of_matching_elements.append(labelling_element)

            # Check if element is in any other equivalence class.
            for comparison_labelling_element in equivalence_classes.keys():
                # Already checked elements in same equivalence class.
                if comparison_labelling_element == labelling_element:
                    continue
                for comparison_element in equivalence_classes[comparison_labelling_element]['class_elements']:
                    if check_element == comparison_element:
                        ec_of_matching_elements.append(comparison_labelling_element)

            if (len(ec_of_matching_elements) != 1) and (
                    ec_of_matching_elements[0] != labelling_element):
                raise Exception(
                    'Element in more than one equivalence class. \nEquivalence_class_of_matching_elements = {0}'.format(
                        ec_of_matching_elements))


########################################################################################################################
def find_outcome_agent(action_sequence, world):
    """
    Uses the transition_matrix in world to find the resulting world state after performing the sequence of minimum
    actions in action_sequence.
    :param action_sequence:
    :param world:
    :return:
    """
    world.reset_state()
    for action in action_sequence[::-1]:
        world.apply_minimum_action(action=action)

    return world.return_state()


########################################################################################################################
def find_element_equivalents_in_state_cayley_table(element, state_cayley_table, world):
    """
    Generates the state Cayley table row and column for the input element then
    :param world:
    :param element:
    :param state_cayley_table: pandas dataframe
    :return:
    """
    # Generate state Cayley table row for element.
    element_row = generate_state_cayley_row(element=element,
                                            state_cayley_table=state_cayley_table,
                                            world=world)

    # Generate state Cayley table column for element.
    element_column = generate_state_cayley_column(element=element,
                                                  state_cayley_table=state_cayley_table,
                                                  world=world)

    # TODO: parallelise this ?
    equivalents_found = set()
    for cayley_element_index in range(len(state_cayley_table.index)):
        cayley_element_row = dict(state_cayley_table.iloc[cayley_element_index])
        cayley_element_column = dict(state_cayley_table.iloc[:, cayley_element_index])

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
    # TODO: change from lists to dicts ?

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
def find_broken_equivalence_classes(candidate_element, ecs, world):
    """
    To check if the candidate element breaks an equivalence class labelled by an element (l):
    1. Find the outcome of (l) \circ ( (c) * w0 ).
    2. For each equivalence class element (e), find the outcome of (e) \circ ( (c) * w0 ).
    3. If (l) \circ ( (c) * w0 ) != (e) \circ ( (c) * w0 ), then the candidate element breaks the
    equivalence class and equivalence class element (e) needs to be split into its own equivalence
    class.

    :param world:
    :param initial_agent_state:
    :param candidate_element:
    :param ecs:
    :return:
    """
    temp_ecs = {}
    for ec_label in ecs.keys():
        # If equivalence class contains a single element, skip it because there are no equivalences to break.
        if len(ecs[ec_label]['class_elements']) == 1:
            continue

        # Find outcome of the equivalence class labelling element acting on w0 after the candidate element:
        # (ec_label \circ a_{C}) * w0.
        # TODO: do I already have this from the equivalence class check ?
        ec_label_outcome = find_outcome_agent(action_sequence=(ec_label + candidate_element),
                                              world=world)

        # Find outcome of each equivalence class element acting on w0 after the candidate element:
        # (ec_element \circ a_{C}) * w_{0}.
        # TODO: convert to list ?
        for ec_element in copy.deepcopy(ecs[ec_label]['class_elements']):
            ec_element_outcome = find_outcome_agent(action_sequence=(ec_element + candidate_element),
                                                    world=world)

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
                        world=world)

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
