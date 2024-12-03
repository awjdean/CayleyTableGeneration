from transformation_algebra.transformation_algebra import TransformationAlgebra
from worlds.graphworlds.graphworld1 import GraphWorld1

world = GraphWorld1()
world.generate_min_action_transformation_matrix()
algebra = TransformationAlgebra(name="test")
algebra.generate_cayley_table_states(world=world, initial_state=(1,))
print(algebra.cayley_table_states)
print(algebra.equiv_classes)
algebra.generate_cayley_table_actions()
print(algebra.cayley_table_actions)
