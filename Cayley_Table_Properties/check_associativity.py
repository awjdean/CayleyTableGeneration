import itertools


def check_associativity(cayley_table):
    """

    :return:
    """
    if cayley_table.cayley_table_actions is None:
        raise Exception(
            'Generate Cayley table using self.generateCayleyTable(parameters) before checking associativity.')

    associativity_info = {'is_associative_algebra': None,
                          'non_associative_elements': [],
                          }

    # Check associativity using associativity equation: a * (b * c) = (a * b) * c
    # Select three elements
    for a, b, c in itertools.product(cayley_table.cayley_table_actions.index,
                                     cayley_table.cayley_table_actions.index,
                                     cayley_table.cayley_table_actions.index):
        ####################################################################################################
        # Calculate LHS of associativity equation: a * (b * c).
        ####################################################################################################
        # Calculate (b * c).
        LHS_bracket_outcome = cayley_table.find_outcome_cayley(left_action=b, right_action=c)
        # Calculate a * (b * c).
        LHS_outcome = cayley_table.find_outcome_cayley(left_action=a, right_action=LHS_bracket_outcome)

        ####################################################################################################
        # Calculate RHS of associativity equation: (a * b) * c.
        ####################################################################################################
        # Calculate (a * b).
        RHS_bracket_outcome = cayley_table.find_outcome_cayley(left_action=a, right_action=b)
        # Calculate (a * b) * c.
        RHS_outcome = cayley_table.find_outcome_cayley(left_action=RHS_bracket_outcome, right_action=c)

        ####################################################################################################
        # Check associativity equation.
        ####################################################################################################
        # Check equation
        if LHS_outcome != RHS_outcome:
            associativity_info['non_associative_elements'].append((a, b, c))

    ################################################################################################################
    # Check if algebra is associative.
    ################################################################################################################
    # Check for overall associativity.
    if len(associativity_info['non_associative_elements']) == 0:
        associativity_info['is_associative_algebra'] = True
    else:
        associativity_info['is_associative_algebra'] = False

    return associativity_info
