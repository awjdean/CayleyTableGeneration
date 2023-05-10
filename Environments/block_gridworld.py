
import itertools
from gridworld import BaseEnvironment, make_world_cyclical, generate_no_walls_transition_matrix

class Gridworld2DBlock(BaseEnvironment):

    def __init__(self, grid_size, initial_block_position, **kwargs):
        super().__init__()

        self._minimum_actions = kwargs.get('minimum_actions', ['1', 'L', 'R', 'U', 'D'])
        self._grid_size = grid_size

        self._initial_block_position = initial_block_position

        self._possible_states = generate_possible_states(grid_size=self._grid_size)


        self.transition_matrix = generate_transition_matrix(grid_size=self._grid_size,
                                                            initial_block_position=self._initial_block_position)


def generate_transition_matrix(grid_size):


    transition_matrix = {}

    """
    action = '1'
    for state in self._possible_states:
        block_position = state[3:4]
        agent_position = state[0:2]
        
        
        
        
        
        transition_matrix[(*agent_position, *block_position, action)] = new_state
    
    
    
    
    """


    return transition_matrix


class Action(Enum):
    NOOP = '1'
    LEFT = 'L'
    RIGHT = 'R'
    UP = 'U'
    DOWN = 'D'

    def apply(self, position):
        if self == self.NOOP:
            return position
        elif self = self




def action_outcome(action, state, grid_size):
    block_position = state[3:4]
    agent_position = state[0:2]

    if action == '1':
        new_state = state

    elif action == 'L':
        agent_position = (agent_position[0] - 1, agent_position[1])
        agent_position = make_world_cyclical(position=agent_position, grid_size=grid_size)

        block_position = (block_position[0] - 1, block_position[1])
        block_position = make_world_cyclical(position=block_position, grid_size=grid_size)

    elif action == 'R':
        agent_position = (agent_position[0] + 1, agent_position[1])
        agent_position = make_world_cyclical(position=agent_position, grid_size=grid_size)

        block_position = (block_position[0] + 1, block_position[1])
        block_position = make_world_cyclical(position=block_position, grid_size=grid_size)

    elif action == 'U':
        agent_position = (agent_position[0], agent_position[1] + 1)
        agent_position = make_world_cyclical(position=agent_position, grid_size=grid_size)

        block_position = (block_position[0], block_position[1] + 1)
        block_position = make_world_cyclical(position=block_position, grid_size=grid_size)





def generate_possible_states(grid_size):
    possible_states = []
    for ax, ay, bx, by in itertools.product(range(grid_size[0]), range(grid_size[1]),
                                            range(grid_size[0]), range(grid_size[1])):
        possible_states.append((ax, ay, bx, by))

    return possible_states

def check_variables(grid_size, block_position, **kwargs):

    # TODO: check block position not in same position as agent - not here ?

    pass



if __name__ == '__main__':
    world = Gridworld2DBlock(grid_size=(2,3),
                             initial_block_position=)
