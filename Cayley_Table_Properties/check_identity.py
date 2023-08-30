import copy
import itertools


def check_identity(cayley_table):
    """
    Uses the action Cayley table to find identity elements, which are stored in identity_info.
    """
    if cayley_table.cayley_table_actions is None:
        raise Exception(
            'Generate Cayley table using self.generateCayleyTable(parameters) before searching for identities.')

    identity_info = {'is_identity_algebra': None,
                                  'left_identities': find_left_identities(cayley_table=cayley_table),
                                  'right_identities': find_right_identities(cayley_table=cayley_table)}

    # Find identities.
    identity_info['identities'] = find_identities(
        left_identities=identity_info['left_identities'],
        right_identities=identity_info['right_identities'])

    # Check there is only a single identity.
    if len(identity_info['identities']) > 1:
        raise Exception(f"More than one identity.\n\tidentities:\t\t{identity_info['identities']}")

    # Record if algebra has an identity.
    if len(identity_info['identities']) == 0:
        identity_info['is_identity_algebra'] = False
    else:
        identity_info['is_identity_algebra'] = True

    return identity_info


def find_left_identities(cayley_table):
    # Create list of potential left identities (e) from the rows/column headings of the Cayley table.
    left_identities = list(copy.deepcopy(cayley_table.cayley_table_actions.index))

    # Test if e is a left identity (e_L * a = a).
    for e_L in cayley_table.cayley_table_actions.index:
        for a in cayley_table.cayley_table_actions.index:
            # Look up the outcome of the LHS of the left identity equation using the action Cayley table.
            LHS_outcome = cayley_table.find_outcome_cayley(left_action=e_L, right_action=a)

            # Outcome for the RHS of the left identity equation is just the element a.
            RHS_outcome = a

            # If the left identity equation is not satisfied, then e_L is not a left identity.
            if LHS_outcome != RHS_outcome:
                left_identities.remove(e_L)
                # Choose another candidate left inverse e_L.
                break

    return left_identities


def find_right_identities(cayley_table):
    # Create list of potential right identities (e) from the rows/column headings of the Cayley table.
    right_identities = list(copy.deepcopy(cayley_table.cayley_table_actions.index))

    # Test if e is a right identity (a * e_R = a)
    for e_R in cayley_table.cayley_table_actions.index:
        for a in cayley_table.cayley_table_actions.index:
            # Look up the outcome of the LHS of the right identity equation using the action Cayley table.
            LHS_outcome = cayley_table.find_outcome_cayley(left_action=a, right_action=e_R)

            # Outcome for the RHS of the right identity equation is just the element a.
            RHS_outcome = a

            # If the right identity equation is not satisfied, then e_R is not a right identity.
            if LHS_outcome != RHS_outcome:
                right_identities.remove(e_R)
                # Choose another candidate right inverse e_R.
                break

    return right_identities


def find_identities(left_identities, right_identities):
    # Identities are elements that are both right identities and left identities.
    identities = []
    for candidate_identity in left_identities:
        if candidate_identity in right_identities:
            identities.append(candidate_identity)

    return identities
