"""
# TODO:
    * turn into functions not a class ?
    * Find outcome from Cayley table function



"""
import copy


from CayleyTable import CayleyTable
from gridworld2D import Gridworld2D


class CayleyTablePropertyChecker(CayleyTable):
    def __init__(self, cayley_table_instance=None):
        super().__init__()

        if cayley_table_instance is not None:
            # TODO: load the cayley table instance as the instance of this function.
            # generateCayleyTable
            self.cayley_table_states = cayley_table_instance.cayley_table_states
            self.cayley_table_actions = cayley_table_instance.cayley_table_actions
            self.state_to_action_label = cayley_table_instance.state_to_action_label
            self.action_label_to_state = cayley_table_instance.action_label_to_state
            self.action_to_state = cayley_table_instance.action_to_state
            self.ecs = cayley_table_instance.ecs
            self.world_params = cayley_table_instance.world_params

        # checkIdentity
        self.identity_info = None

    def checkIdentity(self):

        self.identity_info = {}

        ################################################################################################################
        # Find left identities.
        ################################################################################################################

        # Create list of potential left identities (e) from the rows/column headings of the Cayley table.
        left_identities = list(copy.deepcopy(self.cayley_table_actions.index))

        ### Test if e is a left identity (e * a = a).
        for e in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Find look up the outcome of the LHS of the left identity equation using the action Cayley table.
                LHS_outcome = self.findOutcomeCayley(left_action=e, right_action=a)

                # Outcome for the RHS of the left identity equation is just the element a.
                RHS_outcome = a

                # If the left identity equation is not satisfied, then e is not a left identity.
                if LHS_outcome != RHS_outcome:
                    left_identities.remove(e)
                    break

        self.identity_info['left_identities'] = left_identities

        ################################################################################################################
        # Find right identities.
        ################################################################################################################

        # Create list of potential right identities (e) from the rows/column headings of the Cayley table.
        right_identities = list(copy.deepcopy(self.cayley_table_actions.index))

        ### Test if e is a right identity (a * e = a)
        for e in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Find look up the outcome of the LHS of the right identity equation using the action Cayley table.
                LHS_outcome = self.findOutcomeCayley(left_action=a, right_action=e)

                # Outcome for the RHS of the right identity equation is just the element a.
                RHS_outcome = a

                # If the right identity equation is not satisfied, then e is not a right identity.
                if LHS_outcome != RHS_outcome:
                    right_identities.remove(e)
                    break

        self.identity_info['right_identities'] = right_identities

        ################################################################################################################
        # Find identities.
        ################################################################################################################

        # Identities are elements that are both right identities and left identities.
        identities = []
        for candidate_identity in left_identities:
            if candidate_identity in right_identities:
                identities.append(candidate_identity)

        self.identity_info['identities'] = identities


if __name__ == "__main__":
    print('\nWall at (0.5, 0)')
    table = CayleyTable()

    parameters = {'minimum_actions': ['U', 'R', 'L', 'D', 'D', '1'],
                  'initial_agent_state': (0, 0),
                  'world': Gridworld2D(grid_size=(2, 2), wall_positions=[(0.5, 0)]),
                  'show_calculation': False}  # TODO: remove from here and put in a print function. # TODO: Error when this is True.
    table.generateCayleyTable(**parameters)

    table = CayleyTablePropertyChecker(cayley_table_instance=table)

    print('\nNo walls')
    print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                               len(table.cayley_table_states.columns.values)))
    print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))

    print('\n')
    table.checkIdentity()
    print('\n identity info:')
    for i in table.identity_info.keys():
        print('    {0}:\t\t\t{1}'.format(i, table.identity_info[i]))

