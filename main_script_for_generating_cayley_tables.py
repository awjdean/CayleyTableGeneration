import time

from cayley_table import CayleyTable

from Worlds.gridworld2d_walls import Gridworld2DWalls
from Worlds.gridworld2d_block import Gridworld2DBlock
from Worlds.gridworld2d_consumable import Gridworld2DConsumables
########################################################################################################################

grid_size = (2, 2)
initial_agent_position = (0, 0)
minimum_actions = ['N', 'E', 'W', 'S', 'S', '1']

# Walls
wall_positions = [(0.5, 0)]
wall_strategy = 'identity'

# Block
initial_block_position = (0, 1)

# Consumables
initial_consumable_positions = [(1, 0)]
consumable_strategy = 'masked'

print('Run details:')
print(f"\tgrid_size: {grid_size}")
print(f"\tinitial_agent_state: {initial_agent_position}")
print(f"\tminimum_actions: {minimum_actions}")

####################################################################################################################
# No walls.
####################################################################################################################
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

####################################################################################################################
# Walls.
####################################################################################################################
t0 = time.time()
print(f"\n\nWalls - {wall_strategy}")
print(f"\twall_positions: {wall_positions}")
table = CayleyTable()
parameters = {'minimum_actions': minimum_actions,
              'world': Gridworld2DWalls(grid_size=grid_size,
                                        initial_agent_position=initial_agent_position,
                                        wall_positions=wall_positions,
                                        wall_strategy=wall_strategy),
              }
table.generate_cayley_table(**parameters)
print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
                                                           len(table.cayley_table_states.columns.values)))
print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
print('\nEquivalence classes:')
for i in table.ecs.keys():
    print('\t{0}:\t\t\t{1}'.format(i, table.ecs[i]))
print('\nAction Cayley table equivalence classes:')
for i in table.cayley_table_ecs.keys():
    print('    {0}:\t\t\t{1}'.format(i, table.cayley_table_ecs[i]))
file_name = f"table_{grid_size[0]}x{grid_size[1]}_wall_{str(wall_positions).replace(', ', '_')}_{wall_strategy}_w{str(initial_agent_position).replace(', ', '_')}2"
table.save_cayley_table(file_name=file_name)
print(f'\nTotal time taken: {round(time.time() - t0, 2)}s')

####################################################################################################################
# Block.
####################################################################################################################
# t0 = time.time()
# print('\n\nBlock')
# print(f"\tinitial_block_position: {initial_block_position}")
# table = CayleyTable()
# parameters = {'minimum_actions': minimum_actions,
#               'world': Gridworld2DBlock(grid_size=grid_size,
#                                         initial_agent_position=initial_agent_position,
#                                         initial_block_position=initial_block_position),
#               }
# table.generate_cayley_table(**parameters)
# print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
#                                                            len(table.cayley_table_states.columns.values)))
# print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
# print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
# print('\nEquivalence classes:')
# for i in table.ecs.keys():
#     print('\t{0}:\t\t\t{1}'.format(i, table.ecs[i]))
# print('\nAction Cayley table equivalence classes:')
# for i in table.cayley_table_ecs.keys():
#     print('    {0}:\t\t\t{1}'.format(i, table.cayley_table_ecs[i]))
# file_name = f"table_{grid_size[0]}x{grid_size[1]}_block_w{str((*initial_agent_position, *initial_block_position)).replace(', ', '_')}"
# table.save_cayley_table(file_name=file_name)
# print(f'\nTotal time taken: {round(time.time() - t0, 2)}s')

####################################################################################################################
# Consumables.
####################################################################################################################
# t0 = time.time()
# print('\n\nConsumables')
# table = CayleyTable()
# parameters = {'minimum_actions': ['N', 'E', 'W', 'S', 'S', '1', 'C'],
#               'world': Gridworld2DConsumables(grid_size=grid_size,
#                                               initial_agent_position=initial_agent_position,
#                                               initial_consumable_positions=initial_consumable_positions,
#                                               consumable_strategy=consumable_strategy),
#               }
# table.generate_cayley_table(**parameters)
# print('\nCayley table elements (total: {1}): \n{0}'.format(list(table.cayley_table_states.columns.values),
#                                                            len(table.cayley_table_states.columns.values)))
# print('\nState Cayley table: \n{0}'.format(table.cayley_table_states.to_string()))
# print('\nAction Cayley table: \n{0}'.format((table.cayley_table_actions.to_string())))
# print('\nEquivalence classes:')
# for i in table.ecs.keys():
#     print('\t{0}:\t\t\t{1}'.format(i, table.ecs[i]))
# print('\nAction Cayley table equivalence classes:')
# for i in table.cayley_table_ecs.keys():
#     print('    {0}:\t\t\t{1}'.format(i, table.cayley_table_ecs[i]))
# file_name = f"table_{grid_size[0]}x{grid_size[1]}_consumables_{consumable_strategy}_w{str((*initial_agent_position, *tuple(initial_consumable_positions))).replace(', ', '_')}"
# table.save_cayley_table(file_name=file_name)
# print(f'\nTotal time taken: {round(time.time() - t0, 2)}s')
