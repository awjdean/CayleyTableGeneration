"""
# TODO:
    1. Find order of all elements, then check all possible maps that map elements with the same order together,
     then check if any of these maps are isomorphisms

"""

from CayleyTable import CayleyTable

import copy


########################################################################################################################
# Is Cayley table generating function consistent ?
########################################################################################################################


def get_instance_from_name(name, list_of_instances):
    for t in list_of_instances:
        if t.name == name:
            return t
    return None


def find_same_cayley_tables(list_of_cayley_table_instances):
    info = {'cayley_table_states': [],
            'cayley_table_actions': [],
            'equivalence_classes': [],
            }

    # Find state Cayley tables that are the same.
    for t1 in list_of_cayley_table_instances:
        flag_found_eq = False
        if len(info['cayley_table_states']) == 0:
            info['cayley_table_states'].append([t1.name])
            continue
        for i in info['cayley_table_states']:
            table_instance = get_instance_from_name(name=i[0], list_of_instances=list_of_cayley_table_instances)
            if table_instance.cayley_table_states.equals(t1.cayley_table_states):
                i.append(t1.name)
                flag_found_eq = True
        if not flag_found_eq:
            info['cayley_table_states'].append([t1.name])

    # Find action Cayley tables that are the same.
    for t1 in list_of_cayley_table_instances:
        flag_found_eq = False
        if len(info['cayley_table_actions']) == 0:
            info['cayley_table_actions'].append([t1.name])
            continue
        for i in info['cayley_table_actions']:
            table_instance = get_instance_from_name(name=i[0], list_of_instances=list_of_cayley_table_instances)
            if table_instance.cayley_table_actions.equals(t1.cayley_table_actions):
                i.append(t1.name)
                flag_found_eq = True
        if not flag_found_eq:
            info['cayley_table_actions'].append([t1.name])

    # Find equivalence classes that are the same.
    for t1 in list_of_cayley_table_instances:
        flag_found_eq = False
        if len(info['equivalence_classes']) == 0:
            info['equivalence_classes'].append([t1.name])
            continue
        for i in info['equivalence_classes']:
            table_instance = get_instance_from_name(name=i[0], list_of_instances=list_of_cayley_table_instances)
            if table_instance.ecs == t1.ecs:
                i.append(t1.name)
                flag_found_eq = True
        if not flag_found_eq:
            info['equivalence_classes'].append([t1.name])

    print('\ninfo:')
    print('\tcayley_table_states:\t{0}'.format(info['cayley_table_states']))
    print('\tcayley_table_actions:\t{0}'.format(info['cayley_table_actions']))
    print('\tequivalence_classes:\t{0}'.format(info['equivalence_classes']))

    return info


########
# Comparing table6 with table7.
########

def number_action_cayley_table_elements(table_instance):
    old_table_instance = copy.deepcopy(table_instance)

    old_row_labels = old_table_instance.cayley_table_actions.index
    old_cayley_table_actions = copy.deepcopy(old_table_instance.cayley_table_actions)

    # Create relabelling dictionary.
    relabeling_dict = {}
    for new_label, old_label in enumerate(old_row_labels):
        relabeling_dict[old_label] = new_label

    # Relabel elements in Cayley table.
    new_cayley_table_actions = old_cayley_table_actions.replace(relabeling_dict)

    # Relabel elements in column labels and row labels.
    new_cayley_table_actions = new_cayley_table_actions.rename(columns=relabeling_dict, index=relabeling_dict)

    old_table_instance.cayley_table_actions = new_cayley_table_actions

    return old_table_instance


# def find_isomorphic_map(table_instance1, table_instance2):











# Create Cayley table class instances.
table1 = CayleyTable()
table2 = CayleyTable()
table3 = CayleyTable()
table4 = CayleyTable()
table5 = CayleyTable()
table6 = CayleyTable()
table7 = CayleyTable()

# Load Cayley tables into class instances.
table1.load_cayley_table(file_name='table1')
table2.load_cayley_table(file_name='table2')
table3.load_cayley_table(file_name='table3')
table4.load_cayley_table(file_name='table4')
table5.load_cayley_table(file_name='table5')
table6.load_cayley_table(file_name='table6')
table7.load_cayley_table(file_name='table7')

# Find which Cayley tables are the same
tables = [table1,
          table2,
          table3,
          table4,
          table5,
          table6,
          table7]

table_info = find_same_cayley_tables(list_of_cayley_table_instances=tables)

table6_a = number_action_cayley_table_elements(table6)
table7_a = number_action_cayley_table_elements(table7)

tables_a = [table6_a,
            table7_a]

table_info_a = find_same_cayley_tables(list_of_cayley_table_instances=tables_a)
