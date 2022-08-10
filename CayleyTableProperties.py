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
        self.inverse_info = None

    def checkIdentity(self):
        """
        Uses the action Cayley table to find identity elements, which are stored in self.identity_info.
        """
        if self.cayley_table_actions is None:
            raise Exception(
                'Generate Cayley table using self.generateCayleyTable(parameters) before searching for identities.')

        self.identity_info = {}

        ################################################################################################################
        # Find left identities.
        ################################################################################################################

        # Create list of potential left identities (e) from the rows/column headings of the Cayley table.
        left_identities = list(copy.deepcopy(self.cayley_table_actions.index))

        ### Test if e is a left identity (e_L * a = a).
        for e_L in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the left identity equation using the action Cayley table.
                LHS_outcome = self.findOutcomeCayley(left_action=e_L, right_action=a)

                # Outcome for the RHS of the left identity equation is just the element a.
                RHS_outcome = a

                # If the left identity equation is not satisfied, then e is not a left identity.
                if LHS_outcome != RHS_outcome:
                    left_identities.remove(e_L)
                    break

        self.identity_info['left_identities'] = left_identities

        ################################################################################################################
        # Find right identities.
        ################################################################################################################

        # Create list of potential right identities (e) from the rows/column headings of the Cayley table.
        right_identities = list(copy.deepcopy(self.cayley_table_actions.index))

        ### Test if e is a right identity (a * e_R = a)
        for e_R in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the right identity equation using the action Cayley table.
                LHS_outcome = self.findOutcomeCayley(left_action=a, right_action=e_R)

                # Outcome for the RHS of the right identity equation is just the element a.
                RHS_outcome = a

                # If the right identity equation is not satisfied, then e is not a right identity.
                if LHS_outcome != RHS_outcome:
                    right_identities.remove(e_R)
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

    def checkInverse(self):
        """

        :return:
        """

        if self.cayley_table_actions is None:
            raise Exception(
                'Generate Cayley table using self.generateCayleyTable(parameters) before searching for inverses.')

        if self.identity_info is None:
            raise Exception('Find identities using self.checkInverse() before searching for inverses.')

        self.inverse_info = {}

        ################################################################################################################
        # Find left inverses.
        ################################################################################################################
        left_inverses = {}  # Structure: { a : [(l_inv_a, e_R), ((l_inv_a_2, e_R 2)...], a_2 : None, ...}
        ### Find left inverses for element a (l_inv_a * a = e_R).
        for a in self.cayley_table_actions.index:
            for l_inv_a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the left inverse equation using the action Cayley table.
                LHS_outcome = self.findOutcomeCayley(left_action=l_inv_a, right_action=a)

                # RHS of left inverse equation could be any right identity.
                for e_R in self.identity_info['right_identities']:
                    RHS_outcome = e_R
                    # If the left inverse equation is satisfied, store the details.
                    if LHS_outcome == RHS_outcome:
                        if a in left_inverses.keys():
                            left_inverses[a].append((l_inv_a, e_R))  # TODO: check this works as expected.
                        else:
                            left_inverses[a] = [(l_inv_a, e_R)]
                        # RHS outcome cannot be two different things, therefore break out of loop.
                        break
            # # If no left inverse found for element a, set value in left_inverses to None.
            # if a not in left_inverses.keys():
            #     left_inverses[a] = None

        self.inverse_info['left_inverses'] = left_inverses

        ################################################################################################################
        # Find right inverses.
        ################################################################################################################

        right_inverses = {}  # Structure: { a : [(r_inv_a, e_L), ((r_inv_a_2, e_L_2)...], a_2 : None, ...}

        # Find right inverses for element a (a * r_inv_a = e_L).
        for a in self.cayley_table_actions.index:
            for r_inv_a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the right inverse equation using the action Cayley table.
                LHS_outcome = self.findOutcomeCayley(left_action=a, right_action=r_inv_a)

                # RHS of right inverse equation could be any left identity.
                for e_L in self.identity_info['left_identities']:
                    RHS_outcome = e_L
                    # If the right inverse equation is satisfied, store the details.
                    if LHS_outcome == RHS_outcome:
                        if a in right_inverses.keys():
                            right_inverses[a].append((r_inv_a, e_L))  # TODO: check this works as expected.
                        else:
                            right_inverses[a] = [(r_inv_a, e_L)]
                            # RHS outcome cannot be two different things, therefore break out of loop.
                            break

            # # If no right inverse found for element a, set value in right_inverses to None.
            # if a not in right_inverses.keys():
            #     right_inverses[a] = None

        self.inverse_info['right_inverses'] = right_inverses

        ################################################################################################################
        # Find inverses.
        ################################################################################################################
        # Inverses are elements that are both right inverses and left inverses for the same identity.
        inverses = {}
        for a in self.cayley_table_actions.index:
            if a not in (self.inverse_info['left_inverses'].keys() or self.inverse_info['right_inverses'].keys()):
                continue
            for l_inv_a, e_R in self.inverse_info['left_inverses'][a]:
                for r_inv_a, e_L in self.inverse_info['right_inverses'][a]:
                    # If l_inv_a == r_inv_a, then l_inv_a = r_inv_a is an inverse.
                    if l_inv_a == r_inv_a:
                        # Check if right identity is different to left identity.
                        if e_R != e_L:
                            raise Exception(
                                'Right identity different to left identity: (a, l_inv_a, e_R, r_inv_a, e_L) = ({0}, {1}, {2}. {3}, {4})'.format(
                                    a, l_inv_a, e_R, r_inv_a, e_L))

                        if a in inverses.keys():
                            inverses[a].append((l_inv_a, e_L))  # TODO: check this works as expected.
                        else:
                            inverses[a] = [(l_inv_a, e_L)]

        self.inverse_info['inverses'] = inverses

    def checkAssociate(self):
        """

        :return:
        """





    def printPropertiesInfo(self, **print_parameters):
        identity = print_parameters['identity']
        inverse = print_parameters['inverse']

        if identity:
            print('\n identity info:')
            for i in self.identity_info.keys():
                print('    {0}:\t\t\t{1}'.format(i, self.identity_info[i]))

        if inverse:
            print('\n inverse info:')
            for i in self.inverse_info.keys():
                print('    {0}:\t\t\t{1}'.format(i, self.inverse_info[i]))


if __name__ == "__main__":
    initial_agent_state = (0, 0)
    grid_size = (4, 4)

    ####################################################################################################################
    # No walls
    ####################################################################################################################

    Cayley_table_parameters = {'minimum_actions': ['U', 'R', 'L', 'D', 'D', '1'],
                               'initial_agent_state': initial_agent_state,
                               'world': Gridworld2D(grid_size=grid_size,
                                                    wall_positions=[]),
                               }

    print('\n{0} gridworld, no walls.'.format(str(grid_size)))
    table = CayleyTable()
    table.generateCayleyTable(**Cayley_table_parameters)
    table = CayleyTablePropertyChecker(cayley_table_instance=table)

    print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                               len(table.cayley_table_states.columns.values)))
    print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))

    table.checkIdentity()
    table.checkInverse()

    print_parameters = {'identity': True,
                        'inverse': True,
                        }
    table.printPropertiesInfo(**print_parameters)

    ####################################################################################################################
    # Walls
    ####################################################################################################################
    wall_positions = [(0.5, 0)]

    Cayley_table_parameters = {'minimum_actions': ['U', 'R', 'L', 'D', 'D', '1'],
                               'initial_agent_state': initial_agent_state,
                               'world': Gridworld2D(grid_size=grid_size,
                                                    wall_positions=wall_positions),
                               }

    print('\n{0} grid world, walls at {1}.'.format(str(grid_size), str(wall_positions)))
    table = CayleyTable()

    table.generateCayleyTable(**Cayley_table_parameters)
    table = CayleyTablePropertyChecker(cayley_table_instance=table)

    print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                               len(table.cayley_table_states.columns.values)))
    print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))

    table.checkIdentity()
    table.checkInverse()

    print_parameters = {'identity': True,
                        'inverse': True,
                        }
    table.printPropertiesInfo(**print_parameters)
