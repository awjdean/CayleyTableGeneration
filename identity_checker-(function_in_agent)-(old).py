"""
Identity condition: there exists an element e such that e * a = a and a * e = a for all a in A.




Algorithm:
    -> For each row (or column) element of the Cayley table.
    ->


RETURN: if identity element is present and what that identity element is.





"""

# TODO: put as function of CayleyTable class ?

##############################################
import copy

from CayleyTable import CayleyTable
from gridworld2D import Gridworld2D

##############################################

params = {'initial_agent_state': (0, 0),
          'minimum_actions': ['1', 'R', 'U', 'L', 'D'],
          'world': Gridworld2D(grid_size=(3, 3), wall_positions=[(0.5, 0)]),
          'show_calculation': False,
          }

cayley_table = CayleyTable()
cayley_table.generateCayleyTable(**params)

#####
# Create list of potential left identities from the rows/column headings of the Cayley table.
left_identities = copy.deepcopy(list(cayley_table.cayley_table_actions.index))

### Test if e is a left identity (e * a = a).
for e in cayley_table.cayley_table_actions.index:
    for a in cayley_table.cayley_table_actions.index:
        # Find the outcome of the LHS of the left identity equation.
        left_outcome_state = cayley_table.findOutcomeCayley(left_action=e, right_action=a, return_state_outcome=True)

        # Find the outcome of the RHS of the left identity equation.
        right_outcome_state = cayley_table.findOutcomeCayley(left_action=a, return_state_outcome=True)

        # If the left identity equation is not satisfied, then e is not a left identity element and so remove e from
        # the list of possible left identities and stop checking if e satisfies the left identity equation by
        # breaking out of the e loop.
        if left_outcome_state != right_outcome_state:
            left_identities.remove(
                e)  # TODO: weird error when trying to stop debugger here, but works if the entire file is run ???
            # print('{0} removed'.format(e))
            break
###

# Create list of potential right identities from the rows/column headings of the Cayley table.
right_identities = copy.deepcopy(list(cayley_table.cayley_table_actions.index))

### Test if e is a right identity (a * e = a)
for e in cayley_table.cayley_table_actions.index:
    for a in cayley_table.cayley_table_actions.index:
        # Find the outcome of the LHS of the right identity equation.
        left_outcome_state = cayley_table.findOutcomeCayley(left_action=a, right_action=e, return_state_outcome=True)

        # Find the outcome of the RHS of the right identity equation.
        right_outcome_state = cayley_table.findOutcomeCayley(left_action=a, return_state_outcome=True)

        # If the right identity equation is not satisfied, then e is not a right identity element and so remove e
        # from the list of possible right identities and stop checking if e satisfies the right identity equation by
        # breaking out of the e loop.
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

identity_info = {'left_identities': left_identities,
                 'right_identities': right_identities,
                 'identities': identities}
