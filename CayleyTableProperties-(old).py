from CayleyTable import CayleyTable


class CayleyTablePropertyChecker(CayleyTable):
    def __int__(self):
        super().__init__()
        pass

    def checkIdentity(self):
        # Create list of potential left identities from the rows/column headings of the Cayley table.
        left_identities = copy.deepcopy(list(self.cayley_table_actions.index))

        ### Test if e is a left identity (e * a = a).
        for e in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Find the outcome of the LHS of the left identity equation.
                left_outcome_state = self.findOutcomeCayley(left_action=e, right_action=a, return_state_outcome=True)

                # Find the outcome of the RHS of the left identity equation.
                right_outcome_state = self.findOutcomeCayley(left_action=a, return_state_outcome=True)

                # If the left identity equation is not satisfied, then e is not a left identity element and so remove
                # e from the list of possible left identities and stop checking if e satisfies the left identity
                # equation by breaking out of the e loop.
                if left_outcome_state != right_outcome_state:
                    left_identities.remove(
                        e)  # TODO: weird error when trying to stop debugger here, but works if the entire file is run ???
                    # print('{0} removed'.format(e))
                    break
        ###

        # Create list of potential right identities from the rows/column headings of the Cayley table.
        right_identities = copy.deepcopy(list(self.cayley_table_actions.index))

        ### Test if e is a right identity (a * e = a)
        for e in self.cayley_table_actions.index:
            for a in self.cayley_table_actions.index:
                # Find the outcome of the LHS of the right identity equation.
                left_outcome_state = self.findOutcomeCayley(left_action=a, right_action=e, return_state_outcome=True)

                # Find the outcome of the RHS of the right identity equation.
                right_outcome_state = self.findOutcomeCayley(left_action=a, return_state_outcome=True)

                # If the right identity equation is not satisfied, then e is not a right identity element and so
                # remove e from the list of possible right identities and stop checking if e satisfies the right
                # identity equation by breaking out of the e loop.
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

        self.identity_info = {'left_identities': left_identities,
                              'right_identities': right_identities,
                              'identities': identities}

    def checkInverse(self):
        pass


#######################################################

if __name__ == "__main__":
    table = CayleyTablePropertyChecker()

    parameters = {'minimum_actions': ['1', 'U', 'R', 'L', 'D', 'D'],
                  'initial_agent_state': (0, 0),
                  'world': Gridworld2D(grid_size=(2, 2), wall_positions=[(0.5, 0)]),
                  'show_calculation': False}  # TODO: remove from here and put in a print function. # TODO: Error when this is True.
    table.generateCayleyTable(**parameters)
    print('\n')
    print(table.cayley_table_actions)
    # table.checkIdentity()
    print('\n identity_info: {0}'.format(table.identity_info))
