from worlds.gridworlds_2d.gridworld2d import Gridworld2D

grid = Gridworld2D(grid_shape=(2, 3), initial_agent_state=(0, 0))
print(grid._possible_states)
# print(make_world_cyclical(object_position=(-1, 2), grid_size=(3, 2)))
grid.generate_min_action_transformation_matrix()
matrix = grid._minimum_action_transformation_matrix
print(matrix)
