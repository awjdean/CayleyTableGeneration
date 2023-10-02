import itertools


def check_inverse(cayley_table):
    """

    :return:
    """
    if cayley_table.cayley_table_actions is None:
        raise Exception(
            "Generate Cayley table using self.generateCayleyTable(parameters) before searching for inverses.")

    if cayley_table.identity_info is None:
        raise Exception("Find identities using self.check_identities() before searching for inverses.")

    inverse_info = {'is_inverse_algebra': None}

    ################################################################################################################
    # Find left inverses.
    ################################################################################################################
    inverse_info['left_inverses'] = find_left_inverses(cayley_table=cayley_table)

    ################################################################################################################
    # Find right inverses.
    ################################################################################################################
    inverse_info['right_inverses'] = find_right_inverses(cayley_table=cayley_table)

    ################################################################################################################
    # Find inverses.
    ################################################################################################################
    inverse_info['inverses'] = find_inverses(left_inverses=inverse_info['left_inverses'],
                                             right_inverses=inverse_info['right_inverses'])

    ################################################################################################################
    # Check if algebra has inverses.
    ################################################################################################################
    inverse_info['is_inverse_algebra'] = True
    for algebra_element in cayley_table.cayley_table_actions.index:
        if algebra_element not in inverse_info['inverses']:
            inverse_info['is_inverse_algebra'] = False
            break

    return inverse_info


def find_left_inverses(cayley_table):
    """
    Structure of elements in left_inverses: { a : [(l_inv_a, e_R), ((l_inv_a_2, e_R 2)...], a_2 : None, ...}    # TODO: check "None" is correct.
    """
    left_inverses = {}
    ### Find left inverses for element a (l_inv_a * a = e_R).
    for a, l_inv_a in itertools.product(cayley_table.cayley_table_actions.index,
                                        cayley_table.cayley_table_actions.index):
        # Look up the outcome of the LHS of the left inverse equation using the action Cayley table.
        LHS_outcome = cayley_table.find_outcome_cayley(left_action=l_inv_a, right_action=a)

        # RHS of left inverse equation could be any right identity.
        for e_R in cayley_table.identity_info['right_identities']:
            # If the left inverse equation is satisfied, store the details.
            if LHS_outcome == e_R:
                if a in left_inverses.keys():
                    left_inverses[a].append((l_inv_a, e_R))  # TODO: check this works as expected.
                else:
                    left_inverses[a] = [(l_inv_a, e_R)]
                # RHS outcome cannot be two different things, therefore break out of loop.
                break

    return left_inverses


def find_right_inverses(cayley_table):
    right_inverses = {}  # Structure: { a : [(r_inv_a, e_L), ((r_inv_a_2, e_L_2)...], }

    # Find right inverses for element a (a * r_inv_a = e_L).
    for a, r_inv_a in itertools.product(cayley_table.cayley_table_actions.index,
                                        cayley_table.cayley_table_actions.index):
        # Look up the outcome of the LHS of the right inverse equation using the action Cayley table.
        LHS_outcome = cayley_table.find_outcome_cayley(left_action=a, right_action=r_inv_a)

        # RHS of right inverse equation could be any left identity.
        for e_L in cayley_table.identity_info['left_identities']:
            # If the right inverse equation is satisfied, store the details.
            if LHS_outcome == e_L:
                if a in right_inverses.keys():
                    right_inverses[a].append((r_inv_a, e_L))  # TODO: check this works as expected.
                else:
                    right_inverses[a] = [(r_inv_a, e_L)]
                    # RHS outcome cannot be two different things, therefore break out of loop.
                    break

    return right_inverses


def find_inverses(left_inverses, right_inverses):
    """
    # Structure of items in inverses: { a : [(inv_a, e)], }
    """
    # Inverses are elements that are both right inverses and left inverses for the same identity.
    inverses = {}
    # For each element that either has a left inverse or a right inverse.
    for a in set(left_inverses.keys()) | set(right_inverses.keys()):
        for l_inv_a, e_R in left_inverses[a]:
            for r_inv_a, e_L in right_inverses[a]:
                # If l_inv_a == r_inv_a, then l_inv_a = r_inv_a is an inverse.
                if l_inv_a == r_inv_a:
                    # Check if right identity is different to left identity.
                    if e_R != e_L:
                        raise Exception(
                            f"Right identity different to left identity: (a, l_inv_a, e_R, r_inv_a, e_L): ({a}, {l_inv_a}, {e_R}. {r_inv_a}, {e_L})")

                    if a in inverses.keys():
                        inverses[a].append((l_inv_a, e_L))  # TODO: check this works as expected.
                    else:
                        inverses[a] = [(l_inv_a, e_L)]

    return inverses


if __name__ == '__main__':
    from cayley_table import CayleyTable
    import time
    from Worlds.gridworld2d_walls import Gridworld2DWalls

    grid_size = (4, 1)
    initial_agent_position = (0, 0)
    minimum_actions = ['N', 'E', 'W', 'S', 'S', '1']

    # Walls
    wall_positions = [(0.5, 0)]
    wall_strategy = 'masked'

    # Block
    initial_block_position = (1, 0)

    # Consumables
    initial_consumable_positions = [(1, 0)]  # TODO: check consumable positions are in grid.
    consumable_strategy = 'identity'

    print('Run details:')
    print(f"\tgrid_size: {grid_size}")
    print(f"\tinitial_agent_state: {initial_agent_position}")
    print(f"\tminimum_actions: {minimum_actions}")

    t0 = time.time()
    print('\nNo walls')
    table = CayleyTable()
    parameters = {'minimum_actions': minimum_actions,
                  'world': Gridworld2DWalls(grid_size=grid_size,
                                            initial_agent_position=initial_agent_position),
                  }
    table.generate_cayley_table(**parameters)
    print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                               len(table.cayley_table_states.columns.values)))
    print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
    print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
    print('\nEquivalence classes:')
    for i in table.ecs.keys():
        print('    {0}:\t\t\t{1}'.format(i, table.ecs[i]))
    print('\nAction Cayley table equivalence classes:')
    for i in table.cayley_table_ecs.keys():
        print('    {0}:\t\t\t{1}'.format(i, table.cayley_table_ecs[i]))
    table.save_cayley_table(
        file_name=f"table_{grid_size[0]}x{grid_size[1]}_no_walls_w{str(initial_agent_position).replace(', ', '_')}")
    print(f'\nTotal time taken: {round(time.time() - t0, 2)}s')

    table.check_identity()
    table.check_inverse()
