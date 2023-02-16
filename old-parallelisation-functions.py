

def new_add_element_to_state_cayley_table(element,
                                          state_cayley_table,
                                          find_outcome_agent,
                                          outcome_agent_params,
                                          equivalence_classes=None):
    """
    :param element:
    :param state_cayley_table:
    :param find_outcome_agent:
    :param outcome_agent_params:
    :param equivalence_classes:
    :return:
    """
    _initial_agent_state = outcome_agent_params['initial_agent_state']
    _world = outcome_agent_params['world']

    # ------------------------------------------------------------------------------------------------------------------
    # TODO: change to function?
    # TODO: why is this different to element_row method used in find_element_equivalents_in_state_cayley_table function?
    with concurrent.futures.ThreadPoolExecutor() as executor:
        element_row = dict(executor.map(
            lambda column_label: (column_label, find_outcome_agent(action_sequence=(column_label + element),
                                                                   outcome_agent_params=outcome_agent_params)),
            state_cayley_table.columns))

    # Find state Cayley table row for element ((column_label \circ a_{C}) * w_{0}).
    element_row2 = {}
    for column_label in state_cayley_table.columns:
        outcome = find_outcome_agent(action_sequence=(column_label + element),
                                     outcome_agent_params=outcome_agent_params)
        element_row2[column_label] = outcome

    # Add candidate_element row to state Cayley table.
    element_row = pd.DataFrame([element_row],
                               columns=state_cayley_table.columns,
                               index=[element])
    state_cayley_table = pd.concat([state_cayley_table, element_row])

    # Generate state Cayley table column for element ((a_{C} \circ row_label) * w_{0}).
    element_column = {}
    for row_label in state_cayley_table.index:
        outcome = find_outcome_agent(action_sequence=(element + row_label),
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

def find_element_equivalents_in_state_cayley_table(element, state_cayley_table, outcome_agent_params):
    """
    Generates the state Cayley table row and column for the input element then
    :param element:
    :param state_cayley_table: pandas dataframe
    :param outcome_agent_params:
    :return:
    """
    # TODO: docstring function.
    # TODO: improve efficiency of this.
    # 1. Convert to numpy and use matrix operations ?
    # 2. Store rows and columns for each matrix
    # ------------------------------------------------------------------------------------------------------------------
    element_row = {}
    column_row = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        element_row = dict(executor.map(
            lambda column_label: (column_label, find_outcome_agent(action_sequence=(column_label + element),
                                                                   world_params=outcome_agent_params)),
            state_cayley_table.columns))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        element_column = dict(executor.map(
            lambda row_label: (row_label, find_outcome_agent(action_sequence=(element + row_label),
                                                             world_params=outcome_agent_params)),
            state_cayley_table.index))

    # ------------------------------------------------------------------------------------------------------------------
    # # TODO: this had a concurrence error
    # # Find state Cayley table row for element ((column_label \circ element) * w_{0}).
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     element_row = dict(zip(state_cayley_table.columns, executor.map(
    #         lambda column_label: find_outcome_agent(action_sequence=(column_label + element),
    #                                                 outcome_agent_params=outcome_agent_params),
    #         state_cayley_table.columns)))
    #
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     element_column = dict(zip(state_cayley_table.index, executor.map(
    #         lambda row_label: find_outcome_agent(action_sequence=(element + row_label),
    #                                              outcome_agent_params=outcome_agent_params),
    #         state_cayley_table.index)))

    # ------------------------------------------------------------------------------------------------------------------

    # TODO: delete.
    element_row2 = {}
    for column_label2 in state_cayley_table.columns:
        outcome = find_outcome_agent(action_sequence=(column_label2 + element),
                                     world_params=outcome_agent_params)
        element_row2[column_label2] = outcome
    if element_row != element_row2:
        raise Exception(f'element: {element}\n element_row: {element_row}\n element_row2: {element_row2}')
    # Find state Cayley table column for element ((element \circ row_label) * w_{0}).
    element_column2 = {}
    for row_label2 in state_cayley_table.index:
        outcome = find_outcome_agent(action_sequence=(element + row_label2),
                                     world_params=outcome_agent_params)
        element_column2[row_label2] = outcome
    if element_column != element_column2:
        raise Exception(f'element: {element}\n element_column: {element_column}\n element_column2: {element_column2}')

    # ------------------------------------------------------------------------------------------------------------------
    # Compare row and column of this element to the rows and columns of the elements in the state Cayley table.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        equivalents_found = set(executor.map(
            lambda cayley_element_index: (state_cayley_table.index[cayley_element_index], element) if (dict(
                state_cayley_table.iloc[cayley_element_index]) == element_row) and (dict(
                state_cayley_table.iloc[:, cayley_element_index]) == element_column) else None,
            range(len(state_cayley_table.index))))
    equivalents_found.discard(None)

    # TODO: delete.
    # Compare row and column of this element to the rows and columns of the elements in the state Cayley table.
    equivalents_found2 = set()
    for cayley_element_index in range(len(state_cayley_table.index)):
        cayley_element_row = dict(state_cayley_table.iloc[cayley_element_index])
        cayley_element_column = dict(state_cayley_table.iloc[:, cayley_element_index])

        if (cayley_element_row == element_row) and (cayley_element_column == element_column):
            equivalents_found2.add((state_cayley_table.index[cayley_element_index], element))

    if equivalents_found != equivalents_found2:
        raise Exception(
            f'element: {element}\n equivalents_found: {equivalents_found}\n equivalents_found2: {equivalents_found2}')
    # ------------------------------------------------------------------------------------------------------------------

    return equivalents_found


def old3_find_element_equivalents_in_state_cayley_table(element, state_cayley_table, outcome_agent_params):
    """
    Generates the state Cayley table row and column for the input element then
    :param element:
    :param state_cayley_table: pandas dataframe
    :param outcome_agent_params:
    :return:
    """
    # TODO: docstring function.
    # TODO: improve efficiency of this.
    # 1. Convert to numpy and use matrix operations ?
    # 2. Store rows and columns for each matrix

    # ------------------------------------------------------------------------------------------------------------------

    # Find state Cayley table row for element ((column_label \circ element) * w_{0}).

    element_row = {}
    for column_label in state_cayley_table.columns:
        outcome = find_outcome_agent(action_sequence=(column_label + element),
                                     world_params=outcome_agent_params)
        element_row[column_label] = outcome

    # Find state Cayley table column for element ((element \circ row_label) * w_{0}).
    element_column = {}
    for row_label in state_cayley_table.index:
        outcome = find_outcome_agent(action_sequence=(element + row_label),
                                     world_params=outcome_agent_params)
        element_column[row_label] = outcome

    # ------------------------------------------------------------------------------------------------------------------

    # Compare row and column of this element to the rows and columns of the elements in the state Cayley table.
    equivalents_found = set()
    for cayley_element_index in range(len(state_cayley_table.index)):
        # TODO: check this
        cayley_element_row = dict(state_cayley_table.iloc[cayley_element_index])
        cayley_element_column = dict(state_cayley_table.iloc[:, cayley_element_index])

        if (cayley_element_row == element_row) and (cayley_element_column == element_column):
            equivalents_found.add((state_cayley_table.index[cayley_element_index], element))
    # ------------------------------------------------------------------------------------------------------------------

    return equivalents_found


def old_2find_element_equivalents_in_state_cayley_table(element, state_cayley_table, outcome_agent_params):
    """
    This attempt failed due to
    Generates the state Cayley table row and column for the input element then
    :param element:
    :param state_cayley_table: pandas dataframe
    :param outcome_agent_params:
    :return:
    """
    # TODO: docstring function.
    # TODO: improve efficiency of this.
    # 1. Convert to numpy and use matrix operations ?
    # 2. Store rows and columns for each matrix

    # ------------------------------------------------------------------------------------------------------------------
    # TODO: change to function - also used in add_element_to_cayley_table function

    with concurrent.futures.ThreadPoolExecutor() as executor:
        element_row = list(
            executor.map(lambda column_label: find_outcome_agent(action_sequence=(column_label + element),
                                                                 world_params=outcome_agent_params),
                         state_cayley_table.columns))

        element_column = list(executor.map(lambda row_label: find_outcome_agent(action_sequence=(element + row_label),
                                                                                world_params=outcome_agent_params),
                                           state_cayley_table.index))

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


def old_find_element_equivalents_in_state_cayley_table(element, state_cayley_table, outcome_agent_params):
    """
    Generates the state Cayley table row and column for the input element then
    :param element:
    :param state_cayley_table: pandas dataframe
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
                                     world_params=outcome_agent_params)
        element_row.append(outcome)

    # Find state Cayley table column for element ((element \circ row_label) * w_{0}).
    element_column = []
    for row_label in state_cayley_table.index:
        outcome = find_outcome_agent(action_sequence=(element + row_label),
                                     world_params=outcome_agent_params)
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




