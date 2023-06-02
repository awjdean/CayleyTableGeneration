import itertools
import copy
import pandas
import os
import pickle
import time

from cayley_table_generation import generate_cayley_table
from Cayley_Table_Properties.check_identity import check_identity


########################################################################################################################
class CayleyTable:

    def __init__(self, name=None):
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
        check_identity(cayley_table=self)

    def check_inverse(self):
        pass

    def check_associativity(self):
        pass

    def check_commutativity(self):
        pass

    def find_element_order(self):
        pass

    def print_properties_info(self, **kwargs):
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
                    '\t{0}:\t   {1},   \t{2}'.format(i, self.element_order_info[i][0],
                                                     self.element_order_info[i][1:]))

