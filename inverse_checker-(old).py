"""
Inverse condition: for every element a, there exists an element inv_a such that: a * inv_a = e and inv_a * a = e, where e in an identity element of A.



"""

##############################################
import copy

from CayleyAgent import CayleyAgent
from gridworld2D import Gridworld2D
import itertools

##############################################


params = {'initial_agent_position': (0, 0),
          'table_size': 3,
          'minimum_actions': ['1', 'R', 'U', 'L', 'D'],
          'world': Gridworld2D(grid_size=(3, 3), wall_positions=[(0.5, 0)]),
          'show_calculation': False,
          }

agent = CayleyAgent(**params)
table, state_labelling = agent.generateCayleyTable()


left_inverses = copy.deepcopy(list(table.index))
for a in table.index:       # Test in e is left identity (a * inv_a = e)
    for inv_a in table.index:
        left_outcome_action = table.findOutcomeCayley(first_action=e, second_action=a)
        left_outcome_state = table.action_label_to_state(action_label=left_outcome_action)

        right_outcome_state = table.action_label_to_state(action_label=a)                     #TODO: check issues if e.g., 1 ~ R

        if left_outcome_state != right_outcome_state:
            left_inverses.remove(e)
            break                                                                              #TODO: check 'break' is what is wanted


right_identities = copy.deepcopy(list(table.index))
for e in table.index:       # Test in e is right identity (a * e = a)
    right_identity = True
    for a in table.index:
        left_outcome_action = table.findOutcomeCayley(first_action=a, second_action=e)
        left_outcome_state = table.action_label_to_state(action_label=left_outcome_action)

        right_outcome_state = table.action_label_to_state(action_label=a)                     #TODO: check issues if e.g., 1 ~ R

        if left_outcome_state != right_outcome_state:   # If a * e = a does not hold, then e is not a right identity
            right_identity = False
            break                                                                              #TODO: check 'break' is what is wanted

    if not right_identity:
        right_identities.remove(e)

identities = []
for i in left_inverses:
    if i in right_identities:
        identities.append(i)

