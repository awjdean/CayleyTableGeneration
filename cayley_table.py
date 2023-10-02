import itertools
import copy
import pandas
import os
import pickle
import time

from cayley_table_generation import generate_cayley_table
from Cayley_Table_Properties.check_identity import check_identity
from Cayley_Table_Properties.check_associativity import check_associativity
from Cayley_Table_Properties.check_inverse import check_inverse
from Cayley_Table_Properties.check_commutativity import check_commutativity
from Cayley_Table_Properties.find_element_order import find_element_order


########################################################################################################################
class CayleyTable:

    def __init__(self, name=None):
        self._cayley_table_parameters = None
        self.name = name

        # Cayley table generation.
        self.cayley_table_states = None
        self.cayley_table_actions = None
        self.ecs = None
        self.cayley_table_ecs = None

        self.cayley_table_generation_parameters = None

        # Cayley table properties.
        self.identity_info = None
        self.inverse_info = None
        self.associativity_info = None
        self.element_order_info = None
        self.commutativity_info = None

    def generate_cayley_table(self, minimum_actions, world):
        if (self.cayley_table_actions is not None) or (self.cayley_table_states is not None):
            raise Exception(
                'Cayley table already generated. World used: {0}'.format(self.cayley_table_generation_parameters))

        generate_cayley_table(cayley_table=self, minimum_actions=minimum_actions, world=world)

    def find_outcome_cayley(self, left_action, right_action):
        """
        Uses the Cayley table to find the outcome of the action sequence: left_action \cdot right_action.

        :return: Outcome of left_action \cdot right_action.
        """
        if right_action not in self.cayley_table_actions.index:
            raise Exception('Right action ({0}) not in Cayley table.'.format(right_action))
        if left_action not in self.cayley_table_actions.columns:
            raise Exception('left action ({0}) not in Cayley table.'.format(left_action))

        outcome = self.cayley_table_actions.at[left_action, right_action]
        return outcome

    def save_cayley_table(self, file_name):
        save_dict = {'cayley_table_states': self.cayley_table_states,
                     'cayley_table_actions': self.cayley_table_actions,
                     'equivalence_classes': self.ecs,
                     'cayley_table_parameters': self.cayley_table_generation_parameters,
                     'action_cayley_table_ecs': self.cayley_table_ecs,
                     }
        path = './Saved Cayley tables/'

        if not os.path.exists(path):
            os.makedirs('./Saved Cayley tables/')

        with open(path + file_name, 'wb') as f:
            pickle.dump(save_dict, f, pickle.HIGHEST_PROTOCOL)

        print('\n Cayley table saved as: {0}'.format(file_name))

    def load_cayley_table(self, file_name):
        path = './Saved Cayley tables/'
        with open(path + file_name, 'rb') as f:
            save_dict = pickle.load(f)

        self.cayley_table_states = save_dict['cayley_table_states']
        self.cayley_table_actions = save_dict['cayley_table_actions']
        self.ecs = save_dict['equivalence_classes']
        try:
            self._cayley_table_parameters = save_dict['cayley_table_generation_parameters']
        except AttributeError:
            self._cayley_table_parameters = save_dict['cayley_table_parameters']
        self.cayley_table_ecs = save_dict['action_cayley_table_ecs']

        self.name = file_name

    def check_identity(self):
        self.identity_info = check_identity(cayley_table=self)

    def check_inverse(self):
        self.inverse_info = check_inverse(cayley_table=self)

    def check_associativity(self):
        self.associativity_info = check_associativity(cayley_table=self)

    def check_commutativity(self):
        self.commutativity_info = check_commutativity(cayley_table=self)

    def find_element_order(self):
        self.element_order_info = find_element_order(cayley_table=self)

    def print_properties_info(self, **kwargs):
        """

        """
        identity = kwargs.get('identity', True)
        inverse = kwargs.get('inverse', True)
        associativity = kwargs.get('associativity', True)
        commutativity = kwargs.get('commutativity', True)
        element_order = kwargs.get('element_order', True)

        if identity:
            print("\nidentity info:")
            print(f"\tis_identity_algebra:\t\t{self.identity_info['is_identity_algebra']}")
            print(f"\tleft_identities:\t\t\t{self.identity_info['left_identities']}")
            print(f"\tright_identities:\t\t\t{self.identity_info['right_identities']}")
            print(f"\tidentities:\t\t\t\t\t{self.identity_info['identities']}")

        if inverse:
            print("\ninverse info:")
            print(f"\tis_inverse_algebra:\t\t\t{self.inverse_info['is_inverse_algebra']}")
            print(f"\tleft_inverses:\t\t\t\t{self.inverse_info['left_inverses']}")
            print(f"\tright_inverses:\t\t\t\t{self.inverse_info['right_inverses']}")
            print(f"\tinverses:\t\t\t\t\t{self.inverse_info['inverses']}")

        if associativity:
            print("\nassociativity info:")
            print(f"\tis_associative_algebra:\t\t{self.associativity_info['is_associative_algebra']}")
            print(f"\tnon_associative_elements:\t{self.associativity_info['non_associative_elements']}")

        if commutativity:
            print("\ncommutativity info:")
            print(f"\tis_commutative_algebra:\t\t{self.commutativity_info['is_commutative_algebra']}")
            print(f"\tcommuting_elements:\t\t\t{self.commutativity_info['commuting_elements']}")
            print(f"\tnon_commuting_elements:\t\t{self.commutativity_info['non_commuting_elements']}")
            print(f"\tcommute_with_all:\t\t\t{self.commutativity_info['commute_with_all']}")

        if element_order:
            print("\nelement order info:")
            for i in self.element_order_info.keys():
                print(f"\t{i}:\t   {self.element_order_info[i][0]},   \t{self.element_order_info[i][1:]}")

