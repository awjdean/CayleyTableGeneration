"""
# TODO:
    5. Find disentangled subspaces (commuting subspaces).
"""
import copy
import time

from CayleyTable import CayleyTable


class CayleyTablePropertyChecker(CayleyTable):
    def __init__(self, cayley_table_instance=None):
        super().__init__()

        if cayley_table_instance is not None:
            # generateCayleyTable
            self.cayley_table_states = cayley_table_instance.cayley_table_states
            self.cayley_table_actions = cayley_table_instance.cayley_table_actions
            self.ecs = cayley_table_instance.ecs
            self.world_params = cayley_table_instance._cayley_table_parameters

        # Properties
        self.identity_info = None
        self.inverse_info = None
        self.associativity_info = None
        self.element_order_info = None
        self.commutativity_info = None

    def checkIdentity(self):
        """
        Uses the action Cayley table to find identity elements, which are stored in self.identity_info.
        """
        if self.cayley_table_actions is None:
            raise Exception(
                'Generate Cayley table using self.generateCayleyTable(parameters) before searching for identities.')

        self.identity_info = {'is_identity_algebra': None}

        ################################################################################################################
        # Find left identities.
        ################################################################################################################

        # Create list of potential left identities (e) from the rows/column headings of the Cayley table.
        left_identities = list(copy.deepcopy(self.cayley_table_actions.index))

        ### Test if e is a left identity (e_L * a = a).
        for e_L in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the left identity equation using the action Cayley table.
                LHS_outcome = self.find_outcome_cayley(left_action=e_L, right_action=a)

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
                LHS_outcome = self.find_outcome_cayley(left_action=a, right_action=e_R)

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

        if len(self.identity_info['identities']) > 1:
            raise Exception('More than one identity.\n\tidentities:\t\t{0}'.format(self.identity_info['identities']))

        ################################################################################################################
        # Check if algebra has an identity.
        ################################################################################################################

        if len(self.identity_info['identities']) == 0:
            self.identity_info['is_identity_algebra'] = False
        else:
            self.identity_info['is_identity_algebra'] = True

    def checkInverse(self):
        """

        :return:
        """
        if self.cayley_table_actions is None:
            raise Exception(
                'Generate Cayley table using self.generateCayleyTable(parameters) before searching for inverses.')

        if self.identity_info is None:
            raise Exception('Find identities using self.checkInverse() before searching for inverses.')

        self.inverse_info = {'is_inverse_algebra': None}

        ################################################################################################################
        # Find left inverses.
        ################################################################################################################
        left_inverses = {}  # Structure: { a : [(l_inv_a, e_R), ((l_inv_a_2, e_R 2)...], a_2 : None, ...}
        ### Find left inverses for element a (l_inv_a * a = e_R).
        for a in self.cayley_table_actions.index:
            for l_inv_a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the left inverse equation using the action Cayley table.
                LHS_outcome = self.find_outcome_cayley(left_action=l_inv_a, right_action=a)

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

        self.inverse_info['left_inverses'] = left_inverses

        ################################################################################################################
        # Find right inverses.
        ################################################################################################################

        right_inverses = {}  # Structure: { a : [(r_inv_a, e_L), ((r_inv_a_2, e_L_2)...], }

        # Find right inverses for element a (a * r_inv_a = e_L).
        for a in self.cayley_table_actions.index:
            for r_inv_a in self.cayley_table_actions.index:
                # Look up the outcome of the LHS of the right inverse equation using the action Cayley table.
                LHS_outcome = self.find_outcome_cayley(left_action=a, right_action=r_inv_a)

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

        self.inverse_info['right_inverses'] = right_inverses

        ################################################################################################################
        # Find inverses.
        ################################################################################################################
        # Inverses are elements that are both right inverses and left inverses for the same identity.
        inverses = {}  # Structure: { a : [(inv_a, e)], }
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

        ################################################################################################################
        # Check if algebra has inverses.
        ################################################################################################################
        self.inverse_info['is_inverse_algebra'] = True
        for algebra_element in self.cayley_table_actions.index:
            if algebra_element not in self.inverse_info['inverses']:
                self.inverse_info['is_inverse_algebra'] = False
                break

    def checkAssociativity(self):
        """

        :return:
        """
        if self.cayley_table_actions is None:
            raise Exception(
                'Generate Cayley table using self.generateCayleyTable(parameters) before checking associativity.')

        self.associativity_info = {'is_associative_algebra': None,
                                   'non_associative_elements': [],
                                   }

        # Check associativity using associativity equation: a * (b * c) = (a * b) * c
        # Select three elements
        for a in self.cayley_table_actions.index:
            for b in self.cayley_table_actions.index:
                for c in self.cayley_table_actions.index:
                    ####################################################################################################
                    # Calculate LHS of associativity equation: a * (b * c).
                    ####################################################################################################
                    # Calculate (b * c).
                    LHS_bracket_outcome = self.find_outcome_cayley(left_action=b, right_action=c)
                    # Calculate a * (b * c).
                    LHS_outcome = self.find_outcome_cayley(left_action=a, right_action=LHS_bracket_outcome)

                    ####################################################################################################
                    # Calculate RHS of associativity equation: (a * b) * c.
                    ####################################################################################################
                    # Calculate (a * b).
                    RHS_bracket_outcome = self.find_outcome_cayley(left_action=a, right_action=b)
                    # Calculate (a * b) * c.
                    RHS_outcome = self.find_outcome_cayley(left_action=RHS_bracket_outcome, right_action=c)

                    ####################################################################################################
                    # Check associativity equation.
                    ####################################################################################################

                    # Check equation
                    if LHS_outcome != RHS_outcome:
                        self.associativity_info['non_associative_elements'].append((a, b, c))

        ################################################################################################################
        # Check if algebra is associative.
        ################################################################################################################

        # Check for overall associativity.
        if len(self.associativity_info['non_associative_elements']) == 0:
            self.associativity_info['is_associative_algebra'] = True
        else:
            self.associativity_info['is_associative_algebra'] = False

    def findElementOrder(self):
        """

        :return:
        """
        if self.cayley_table_actions is None:
            raise Exception(
                'Generate Cayley table using self.generateCayleyTable(parameters) before finding element orders.')

        if self.identity_info is None:
            raise Exception('Find identities using self.checkInverse() before finding element orders.')

        self.element_order_info = {}  # Structure: { a_1 : (order n, order_search), a_2 : (float('inf'), order_search, (cycle_start, cycle_length)) }

        # Check if identity element exists.
        if len(self.identity_info['identities']) == 0:
            self.element_order_info = 'No identity, therefore cannot calculate element orders.'

        # The maximum order an element can have, if it has a finite order, is the number of elements in the algebra.
        max_order = len(self.cayley_table_actions.index)
        for a in self.cayley_table_actions.index:
            for e in self.identity_info['identities']:
                n = 1
                order_search = [a]

                # If an element is an identity element, then it has an order of 1.
                if a == e:
                    self.element_order_info[a] = (n, order_search)
                    continue

                a_outcome = a
                while True:
                    n += 1

                    a_outcome = self.find_outcome_cayley(left_action=a, right_action=a_outcome)

                    # If the element a_outcome is an identity element, then element a has an order of n.
                    if a_outcome == e:
                        self.element_order_info[a] = (n, order_search)
                        order_search.append(a_outcome)
                        break

                    # If the element order search for element a returns to an element seen before without reaching an
                    # identity, then the search for the order of a has hit a cycle and so a has infinite order.
                    if a_outcome in order_search:
                        cycle_start = a_outcome
                        cycle_length = order_search[::-1].index(a_outcome) + 1
                        self.element_order_info[a] = (float('inf'), order_search, (cycle_start, cycle_length))
                        break

                    order_search.append(a_outcome)

                    # CHECK.
                    if n > max_order:
                        self.element_order_info[a] = ('$infty', 'max_order')
                        raise Exception(
                            'Max element order ({0}} reached. (a, order_search)'.format(max_order, a, order_search))

    def checkCommutativity(self):
        """

        :return:
        """
        self.commutativity_info = {'is_commutative_algebra': None,
                                   'commuting_elements': {},
                                   'non_commuting_elements': {},
                                   'commute_with_all': [],
                                   }

        ################################################################################################################
        # Find commuting elements.
        ################################################################################################################
        # Two elements a,b commute if they satisfy the commutativity equation: a * b = b * a.
        for a in self.cayley_table_actions.index:
            self.commutativity_info['commuting_elements'][a] = []
            self.commutativity_info['non_commuting_elements'][a] = []
            for b in self.cayley_table_actions.index:
                # Calculate the LHS of the commutativity equation (a * b).
                LHS_outcome = self.find_outcome_cayley(left_action=a, right_action=b)

                # Calculate the RHS of the commutativity equation (b * a).
                RHS_outcome = self.find_outcome_cayley(left_action=b, right_action=a)

                # If LHS_outcome = RHS_outcome, then store that a,b commute.
                if LHS_outcome == RHS_outcome:
                    self.commutativity_info['commuting_elements'][a].append(b)
                else:
                    self.commutativity_info['non_commuting_elements'][a].append(b)

        ################################################################################################################
        # Check if algebra is commutative.
        ################################################################################################################
        # For the algebra to be commutative, every pair of elements must commute.

        if len(self.commutativity_info['non_commuting_elements'].keys()) > 0:
            self.commutativity_info['is_commutative_algebra'] = True
        else:
            self.commutativity_info['is_commutative_algebra'] = False

        ################################################################################################################
        # Find elements that commute with all other elements.
        ################################################################################################################
        for a in self.cayley_table_actions.index:
            if set(self.commutativity_info['commuting_elements'][a]) == set(self.cayley_table_actions.index):
                self.commutativity_info['commute_with_all'].append(a)

    def printPropertiesInfo(self, **kwargs):
        """

        :param print_parameters:
        :return:
        """
        identity = kwargs.get('identity', True)
        inverse = kwargs.get('inverse', True)
        associativity = kwargs.get('associativity', True)
        commutativity = kwargs.get('commutativity', True)
        element_order = kwargs.get('element_order', True)

        if identity:
            print('\nidentity info:')
            print('\tis_identity_algebra:\t\t{0}'.format(self.identity_info['is_identity_algebra']))
            print('\tleft_identities:\t\t\t{0}'.format(self.identity_info['left_identities']))
            print('\tright_identities:\t\t\t{0}'.format(self.identity_info['right_identities']))
            print('\tidentities:\t\t\t\t\t{0}'.format(self.identity_info['identities']))

        if inverse:
            print('\ninverse info:')
            print('\tis_inverse_algebra:\t\t\t{0}'.format(self.inverse_info['is_inverse_algebra']))
            print('\tleft_inverses:\t\t\t\t{0}'.format(self.inverse_info['left_inverses']))
            print('\tright_inverses:\t\t\t\t{0}'.format(self.inverse_info['right_inverses']))
            print('\tinverses:\t\t\t\t\t{0}'.format(self.inverse_info['inverses']))

        if associativity:
            print('\nassociativity info:')
            print('\tis_associative_algebra:\t\t{0}'.format(self.associativity_info['is_associative_algebra']))
            print('\tnon_associative_elements:\t{0}'.format(self.associativity_info['non_associative_elements']))

        if commutativity:
            print('\ncommutativity info:')
            print('\tis_commutative_algebra:\t\t{0}'.format(self.commutativity_info['is_commutative_algebra']))
            print('\tcommuting_elements:\t\t\t{0}'.format(self.commutativity_info['commuting_elements']))
            print('\tnon_commuting_elements:\t\t{0}'.format(self.commutativity_info['non_commuting_elements']))
            print('\tcommute_with_all:\t\t\t{0}'.format(self.commutativity_info['commute_with_all']))

        if element_order:
            print('\nelement order info:')
            for i in self.element_order_info.keys():
                print(
                    '\t{0}:\t   {1},   \t{2}'.format(i, self.element_order_info[i][0], self.element_order_info[i][1:]))


if __name__ == "__main__":
    # initial_agent_state = (0, 0)
    # grid_size = (3, 3)
    #
    # ####################################################################################################################
    # # No walls
    # ####################################################################################################################
    # t0 = time.time()
    #
    # Cayley_table_parameters = {'minimum_actions': ['U', 'R', 'L', 'D', '1'],
    #                            'initial_agent_state': initial_agent_state,
    #                            'world': Gridworld2D(grid_size=grid_size,
    #                                                 wall_positions=[]),
    #                            }
    #
    # print('\n{0} gridworld, no walls.'.format(str(grid_size)))
    # # Create Cayley table instance.
    # table = CayleyTable()
    # # Generate Cayley table.
    # table.generate_cayley_table(**Cayley_table_parameters)
    # # Load Cayley table into the property checker.
    # table = CayleyTablePropertyChecker(cayley_table_instance=table)
    #
    # print('\nCayley table elements (total: {1}):\t{0}'.format(list(table.cayley_table_states.columns.values),
    #                                                           len(table.cayley_table_states.columns.values)))
    # print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    # print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
    #
    # table.checkIdentity()
    # table.checkInverse()
    # table.checkAssociativity()
    # table.checkCommutativity()
    # table.findElementOrder()
    #
    # print_parameters = {'identity': True,
    #                     'inverse': True,
    #                     'associativity': True,
    #                     'element_order': True,
    #                     'commutativity': True,
    #                     }
    # table.printPropertiesInfo(**print_parameters)
    #
    # print('\nTime taken: {0:0.2f}s'.format(time.time()-t0))
    # print('\n#########################################################################################################')
    # ####################################################################################################################
    # # Walls
    # ####################################################################################################################
    # t0 = time.time()
    #
    # wall_positions = [(0.5, 0)]
    #
    # Cayley_table_parameters = {'minimum_actions': ['U', 'R', 'L', 'D', '1'],
    #                            'initial_agent_state': initial_agent_state,
    #                            'world': Gridworld2D(grid_size=grid_size,
    #                                                 wall_positions=wall_positions),
    #                            }
    #
    # print('\n{0} grid world, walls at {1}.'.format(str(grid_size), str(wall_positions)))
    # # Create Cayley table instance.
    # table2 = CayleyTable()
    # # Generate Cayley table.
    # table2.generate_cayley_table(**Cayley_table_parameters)
    # # Load Cayley table into the property checker.
    # table2 = CayleyTablePropertyChecker(cayley_table_instance=table2)
    #
    # print('\nCayley table elements (total: {1}):\t{0}'.format(list(table2.cayley_table_states.columns.values),
    #                                                           len(table2.cayley_table_states.columns.values)))
    # print('\nState Cayley table: \n{0}'.format(table2.cayley_table_states.to_string()))
    # print('\nAction Cayley table: \n{0}'.format((table2.cayley_table_actions.to_string())))
    #
    # table2.checkIdentity()
    # table2.checkInverse()
    # table2.checkAssociativity()
    # table2.checkCommutativity()
    # table2.findElementOrder()
    #
    # table2.printPropertiesInfo(**print_parameters)
    #
    # print('\nTime taken: {0:0.2f}s'.format(time.time() - t0))

    ####################################################################################################################
    # Load table and perform tests
    ####################################################################################################################

    grid_size = (2, 2)
    wall_positions = []
    initial_agent_state = (0, 0)
    minimum_actions = ['U', 'R', 'L', 'D', 'D', '1']

    t0 = time.time()
    if len(wall_positions) == 0:
        table_name = f"table_{grid_size[0]}x{grid_size[1]}_no_walls_w{str(initial_agent_state).replace(', ', '_')}"
        # TODO: replace thing for agent state ?
    else:
        table_name = f"table_{grid_size[0]}x{grid_size[1]}_wall_{str(wall_positions).replace(', ', '_')}_identity_w{str(initial_agent_state).replace(', ', '_')}"

    table = CayleyTable()
    table.load_cayley_table(file_name=table_name)
    property_checker = CayleyTablePropertyChecker(cayley_table_instance=table)
    property_checker.checkIdentity()
    property_checker.checkInverse()
    property_checker.checkAssociativity()
    property_checker.checkCommutativity()
    property_checker.findElementOrder()

    property_checker.printPropertiesInfo()

    print('\nTime taken: {0:0.2f}s'.format(time.time() - t0))
