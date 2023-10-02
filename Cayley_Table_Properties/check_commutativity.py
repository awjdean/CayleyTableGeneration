def check_commutativity(cayley_table):
    """

    :return:
    """
    commutativity_info = {
        'is_commutative_algebra': None,
        'commuting_elements': (find_commuting_elements(cayley_table=cayley_table))[0],
        'non_commuting_elements': (find_commuting_elements(cayley_table=cayley_table))[1],
        'commute_with_all': []}

    ################################################################################################################
    # Find elements that commute with all other elements.
    ################################################################################################################

    commutativity_info['commute_with_all'] = find_elements_that_commute_with_all_elements(
        cayley_table=cayley_table,
        commuting_elements=commutativity_info['commuting_elements']
    )

    ################################################################################################################
    # Check if algebra is commutative.
    ################################################################################################################
    # For the algebra to be commutative, every pair of elements must commute.

    try:
        assert len(commutativity_info['commute_with_all']) <= len(cayley_table.cayley_table_actions.index)
    except AssertionError:
        raise Exception("Too many elements in commute_with_all.")

    if len(commutativity_info['commute_with_all']) == len(cayley_table.cayley_table_actions.index):
        commutativity_info['is_commutative_algebra'] = True
    else:
        commutativity_info['is_commutative_algebra'] = False

    return commutativity_info


def find_commuting_elements(cayley_table):
    commuting_elements, non_commuting_elements = {}, {}
    # Two elements a,b commute if they satisfy the commutativity equation: a * b = b * a.
    for a in cayley_table.cayley_table_actions.index:
        commuting_elements[a] = []
        non_commuting_elements[a] = []
        for b in cayley_table.cayley_table_actions.index:
            # Calculate the LHS of the commutativity equation (a * b).
            LHS_outcome = cayley_table.find_outcome_cayley(left_action=a, right_action=b)

            # Calculate the RHS of the commutativity equation (b * a).
            RHS_outcome = cayley_table.find_outcome_cayley(left_action=b, right_action=a)

            # If LHS_outcome = RHS_outcome, then store that a,b commute.
            if LHS_outcome == RHS_outcome:
                commuting_elements[a].append(b)
            else:
                non_commuting_elements[a].append(b)

    return commuting_elements, non_commuting_elements


def find_elements_that_commute_with_all_elements(cayley_table, commuting_elements):
    commute_with_all = []
    for a in cayley_table.cayley_table_actions.index:
        if set(commuting_elements[a]) == set(cayley_table.cayley_table_actions.index):
            commute_with_all.append(a)

    return commute_with_all
