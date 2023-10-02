# Generating Cayley tables

To generate a Cayley table:
1. Initiate an instance of CayleyTable [ table = CayleyTable() ].
2. Define parameters for the Cayley table
   1. Minimum actions: ['N', 'E', 'W', 'S', 'S', '1', 'C'].
   2. World class instance.
3. Generate the Cayley table [ table.generate_cayley_table(**parameters) ].

# Worlds
## Gridworld2DWalls

See main_script_for_generating_cayley_tables.py for examples.

Gridworld2DWalls(grid_size=grid_size,
                 initial_agent_position=initial_agent_position,
                 wall_positions=wall_positions,
                 wall_strategy=wall_strategy)

grid_size - the size of the gridworld, 2D integer tuple.
initial_agent_position - the initial position of the agent, 2D integer tuple.
wall_position - the position of the walls as a list of position tuples.
                Each position has a half integer value and an integer value so that it is located between integer positions on the grid.
wall_strategy - 'identity' for treating restricted actions like the identity element,
                'masked' for masking restricted actions.

## Gridworld2DBlock

Gridworld2DBlock(grid_size=grid_size,
                 initial_agent_position=initial_agent_position,
                 initial_block_position=initial_block_position)

grid_size - the size of the gridworld, 2D integer tuple.
initial_agent_position - the initial position of the agent, 2D integer tuple.
initial_block_position - the initial position of the movable block, 2D integer tuple.

## Gridworld2DConsumables

Gridworld2DConsumables(grid_size=grid_size,
                       initial_agent_position=initial_agent_position,
                       initial_consumable_positions=initial_consumable_positions,
                       consumable_strategy=consumable_strategy)

grid_size - the size of the gridworld, 2D integer tuple.
initial_agent_position - the initial position of the agent, 2D integer tuple.
initial_consumable_positions - list of 2D tuples, where each 2D tuple is the initial position of a consumable.
consumable_strategy - 'identity' for treating restricted actions like the identity element,
                      'masked' for masking restricted actions.

## GraphWorld

You can also specify your own custom world by modifying the GraphWorld class.
You would need to modify the following:
   1. minimum_actions - list of minimum actions for your world.
   2. self._possible_states - list of tuples representing each possible world state of your world.
   3. initial_agent_state - the initial state you want to build your Cayley tables from.
   4. generate_transition_matrix() function - you need to define the end state when each minimum action is applied to each state.


# Property checkers
These functions extract properties of A/\sim from its Cayley tables.

## check_identity
Searches for right and left identities for each element of A/\sim.
**To run:** table.check_identity()

## check_inverse
Searches for right and left inverses for each element of A/\sim.
**To run:** able.check_inverse()

## check_associativity
Checks if A/\sim satisfies associativity.
**To run:** table.check_associativity()

## check_commutativity
Checks if A/\sim satisfies commutativity.
**To run:** table.check_commutativity()

## find_element_order
Finds the order of each element of $A/\sim.
**To run:** table.find_element_order()

## print_properties_info
This prints out all the collected information about the properties of the A/\sim algebra.
**To run:** table.print_properties_info()
