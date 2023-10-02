


class GraphWorld1:

    def __init__(self, initial_agent_state=(1,), **kwargs):

        self._minimum_actions = kwargs.get('minimum_actions', ['1', 'a', 'b'])

        self._initial_agent_state = initial_agent_state
        self._current_state = initial_agent_state

        self._possible_states = [(1,), (2,), (3,)]
        self.transition_matrix = generate_transition_matrix()

    def reset_state(self):
        self._current_state = self._initial_agent_state

    def return_state(self):
        return self._current_state

    def apply_minimum_action(self, action):
        self._current_state = self.transition_matrix[(*self._current_state, action)]

    def draw_world(self):
        print("Function not defined.")


def generate_transition_matrix():
    transition_matrix = {}

    # 1 action.
    action = '1'
    transition_matrix[(*(1,), action)] = (1,)
    transition_matrix[(*(2,), action)] = (2,)
    transition_matrix[(*(3,), action)] = (3,)

    # a action.
    action = 'a'
    transition_matrix[(*(1,), action)] = (2,)
    transition_matrix[(*(2,), action)] = (3,)
    transition_matrix[(*(3,), action)] = (1,)

    # b action.
    action = 'b'
    transition_matrix[(*(1,), action)] = (2,)
    transition_matrix[(*(2,), action)] = (1,)
    transition_matrix[(*(3,), action)] = (3,)

    return transition_matrix

if __name__ == '__main__':
    world = GraphWorld1(initial_agent_state=(1,))

    for key in world.transition_matrix.keys():
        print(f"{key}: {world.transition_matrix[key]}")
