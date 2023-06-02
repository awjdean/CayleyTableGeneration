import itertools
import numpy as np

from OLD_cayley_table_generation import CayleyTable

########################################################################################################################
# Basic checks.
"""

"""
########################################################################################################################


########################################################################################################################
# Method 1 - using state Cayley table.
"""
Pseudo code:
    1. For each row/column labelling element $a1$ in cayley_table1:
        a. Get state Cayley table row for $a1$ from cayley_table1.
        b. Get state Cayley table column for $a1$ from cayley_table1.
        c. For each row/column labelling element $a2$ in cayley_table2:
            i. If $a1$ in 
            ii. Get state Cayley table row for $a2$ from cayley_table2.
            iii. Get state Cayley table column for $a2$ from cayley_table2.
            iv. If $a1$ row == $a2$ row and $a1$ column == $a2$ column:
                (1) Store info
                (2) flag_equivalent_element_found = True
        d. If flag_equivalent_element_found != True:
            i. 
"""


########################################################################################################################

def check_isomorphic_method1(cayley_table1: CayleyTable, cayley_table2: CayleyTable):
    isomorphism_info = {'isomorphism_exists': None,
                        'equivalent_elements_map': [],
                        'equivalent_elements_map_injective': None,
                        'equivalent_elements_map_surjective': None
                        }

    # Find equivalent elements map.
    for a1 in cayley_table1.cayley_table_states.index:
        flag_equivalent_element_found = False
        a1_row = cayley_table1.cayley_table_states.loc[a1]
        a1_column = cayley_table1.cayley_table_states[a1]

        for a2 in cayley_table2.cayley_table_states.index:
            a2_row = cayley_table2.cayley_table_states.loc[a2]
            a2_column = cayley_table2.cayley_table_states[a2]

            if list(a1_row) == list(a2_row) and list(a1_column) == list(a2_column):
                isomorphism_info['equivalent_elements_map'].append((a1, a2))
                flag_equivalent_element_found = True

        # If no equivalent element for a1 is found in cayley_table2, then the equivalent_elements_map maps that
        # element to None.
        if not flag_equivalent_element_found:
            isomorphism_info['equivalent_elements_map'].append((a1, None))

    # Check equivalent_elements_map is surjective.
    # If every element a2 in cayley_table2 is in at least one RHS of equivalent_elements_map assignments, then
    # equivalent_elements_map is surjective.
    flag_surjective = True
    for a2 in cayley_table2.cayley_table_states.index:
        flag_a2_found = False
        for equivalent_elements_map_assignment in isomorphism_info['equivalent_elements_map']:
            if equivalent_elements_map_assignment[1] == a2:
                flag_a2_found = True
                break
        if not flag_a2_found:
            isomorphism_info['equivalent_elements_map'].append((None, a2))
            flag_surjective = False
    if flag_surjective:
        isomorphism_info['equivalent_elements_map_surjective'] = True
    else:
        isomorphism_info['equivalent_elements_map_surjective'] = False

    # Check equivalent_elements_map is injective.
    # If no None in RHS of equivalent_elements_map assignments, then equivalent_elements_map is injective.
    flag_injective = True
    for equivalent_elements_map_assignment in isomorphism_info['equivalent_elements_map']:
        if equivalent_elements_map_assignment[1] == None:
            flag_injective = False
    if flag_injective:
        isomorphism_info['equivalent_elements_map_injective'] = True
    else:
        isomorphism_info['equivalent_elements_map_injective'] = False

    # Check equivalent_elements_map is isomorphic.
    if isomorphism_info['equivalent_elements_map_surjective'] and isomorphism_info['equivalent_elements_map_injective']:
        isomorphism_info['isomorphism_exists'] = True
    else:
        isomorphism_info['isomorphism_exists'] = False

    return isomorphism_info


########################################################################################################################
# Method 2 - using action Cayley table only.
"""

"""


def are_cayley_tables_isomorphic_method2(cayley_table1: CayleyTable, cayley_table2: CayleyTable):
    print(f"\nPerforming isomorphic test.")
    table1 = cayley_table1.cayley_table_actions
    table2 = cayley_table2.cayley_table_actions

    isomorphism_info = {'is_isomorphic': None,
                        'same_num_elements': None,
                        }

    # Check that Cayley tables have the same number of elements.
    if table1.shape != table2.shape:
        isomorphism_info['same_num_elements'] = False
        isomorphism_info['is_isomorphic'] = False
        return isomorphism_info
    else:
        isomorphism_info['same_num_elements'] = True
        print(f"Cayley tables have same number of labelling elements.")

    # Find order of elements.




    elements = set(table1.values.flatten())
    for permutation in itertools.permutations(elements):
        transformed_table2 = table2.replace(list(elements), list(permutation))

        if np.array_equal(transformed_table2.values, table1.values):
            isomorphism_info['is_isomorphic'] = True
            return isomorphism_info

    isomorphism_info['is_isomorphic'] = False
    return isomorphism_info


########################################################################################################################


########################################################################################################################
# Tests
########################################################################################################################
if __name__ == '__main__':
    pass

    # TODO: Tests
    #   1. Test that the same Cayley table is equivalent.
    #   2. Test consumable Cayley tables are equivalent.

    ####################################################################################################################
    # Test that same Cayley tables are equivalent.
    ####################################################################################################################
    table1_name = "table_2x2_wall_[(0.5_0)_(0.5_0)]_masked_w(0_0)1"
    table2_name = "table_2x2_wall_[(0.5_0)_(0.5_0)]_masked_w(0_0)2"

    # Load Cayley table 1.
    table1 = CayleyTable()
    table1.load_cayley_table(file_name=table1_name)

    # Load Cayley table 2.
    table2 = CayleyTable()
    table2.load_cayley_table(file_name=table2_name)

    # Isomorphism test
    isomorphism_info = are_cayley_tables_isomorphic_method2(cayley_table1=table1,
                                                            cayley_table2=table2)
    print(isomorphism_info)
